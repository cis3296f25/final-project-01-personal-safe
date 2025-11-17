from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty, StringProperty
from kivy.logger import Logger
import threading
from kivy.clock import Clock
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from core.vault import Vault
from core import masterPassword as mp
from app_state import app_state


class LoginScreen(Screen):
    error_text = StringProperty("")  # Bound to error label
    pwd_field = ObjectProperty(None)  # Bound to password TextInput

    def on_pre_enter(self, *args):
        # Reset UI state
        self.error_text = ""
        if self.pwd_field:
            self.pwd_field.text = ""
        Logger.info("LoginScreen: ready")

    def on_pre_enter(self, *args):
        self.error_text = ""
        if self.pwd_field:
            self.pwd_field.text = ""
        Logger.info("LoginScreen: ready")

    def do_login(self):
        pwd = (self.pwd_field.text or "").strip() if self.pwd_field else ""
        if not pwd:
            self.error_text = "Enter master password"
            return
        try:
            # If master hash doesn't exist, create it with provided password
            if not mp.os.path.exists(mp.masterHashFile):
                mp.createMasterPassword(pwd)
            else:
                if not mp.verifyMasterPassword(pwd):
                    self.error_text = "Incorrect password"
                    return

            # Initialize vault with current password
            app_state.vault = Vault(pwd)
            app_state.master_password = pwd

            Logger.info("Login: authenticated; vault initialized")
            # If a home screen exists, navigate there; otherwise stay
            if "HOME" in self.manager.screen_names:
                self.manager.current = "HOME"
        except Exception as e:
            Logger.exception("Login error")
            self.error_text = f"Error: {e}"

    def on_submit(self):
        self.do_login()

    def forgot_password(self):
        """Called by the KV button on_release: root.forgot_password()"""
        if getattr(self, "_forgot_sending", False):
            return
        self._forgot_sending = True
        try:
            rec = mp.loadRecovery()  #must return dict-like with 'email'
            email = rec.get("email") if isinstance(rec, dict) else None
        except Exception as e:
            Logger.exception("forgot_password: loadRecovery failed")
            self._show_popup("Error", f"Failed to read recovery settings: {e}")
            self._forgot_sending = False
            return

        if not email:
            self._show_popup("No recovery email", "No recovery email configured. Go to Settings and set one.")
            self._forgot_sending = False
            return

        #create popup
        sending_popup = Popup(title="Sending...", content=Label(text=f"Sending to {email}"), size_hint=(0.7, 0.2), auto_dismiss=False)
        sending_popup.open()

        #smtp config from app_state if available
        smtp_config = getattr(app_state, "smtp_config", None)

        #sending in background thread
        thread = threading.Thread(target=self._forgot_send_thread, args=(email, smtp_config, sending_popup), daemon=True)
        thread.start()

    def _send_recovery_thread(self, email, smtp_config, popup):
        try:
            if smtp_config is None:
                import secrets
                token = secrets.token_urlsafe(32)
                mp.storeTokenHash(token, ttl_seconds=3600)
                Clock.schedule_once(lambda dt: self._on_send_result(True, f"DEV TOKEN: {token}", popup), 0)
                return

            ok, msg = mp.generate_and_send_recovery(smtp_config, email, ttl_seconds=3600)
            Clock.schedule_once(lambda dt: self._on_send_result(ok, msg, popup), 0)
        except Exception as e:
            Logger.exception("forgot_password: unexpected error")
            Clock.schedule_once(lambda dt: self._on_send_result(False, f"Internal error: {e}", popup), 0)

    def _on_send_result(self, ok: bool, msg: str, popup: Popup):
        popup.dismiss()
        self._forgot_sending = False
        if ok:
            if msg.startswith("DEV TOKEN:"):
                token = msg.split("DEV TOKEN: ", 1)[-1]
                self._show_popup("Dev token (testing only)", f"Use this token to reset: {token}")
            else:
                self._show_popup("Recovery email sent", f"A recovery email was sent to {msg if isinstance(msg, str) else 'your email'}.")
        else:
            self._show_message("Send failed", f"Failed to send recovery email: {msg}")

    def _show_message(self, title: str, message: str):
        box = BoxLayout(orientation="vertical", padding=10)
        box.add_widget(Label(text=message))
        btn = Button(text="OK", size_hint=(1, 0.25))
        box.add_widget(btn)
        p = Popup(title=title, content=box, size_hint=(0.8, 0.4))
        btn.bind(on_release=lambda *_: p.dismiss())
        p.open()
