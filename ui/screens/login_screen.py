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
        try:
            rec = mp.loadRecovery()  # should return dict with "email"
        except Exception as e:
            Logger.exception("Failed loadRecovery")
            self._show_message("Error", f"Failed to read recovery settings: {e}")
            return

        email = rec.get("email") if isinstance(rec, dict) else None
        if not email:
            self._show_message("No recovery email", "No recovery email configured. Set one in Settings.")
            return
        sending_popup = Popup(title="Sending...", content=Label(text=f"Sending recovery email to {email}"), size_hint=(0.7, 0.2), auto_dismiss=False)
        sending_popup.open()
        thread = threading.Thread(target=self._send_recovery_thread, args=(email, sending_popup), daemon=True)
        thread.start()

    def _send_recovery_thread(self, email, popup):
        #smtpConfig should come from secure storage / app_state. Provide one or ask user earlier.
        smtpConfig = getattr(app_state, "smtp_config", None)
        #If you don't have smtp_config in app_state, you can prompt the user in Settings to provide it,
        #or pass None for testing (but mp.generate_and_send_recovery may require it).
        try:
            ok, msg = mp.generate_and_send_recovery(smtpConfig, email, ttl_seconds=3600)
        except Exception as e:
            Logger.exception("generate_and_send_recovery failed")
            ok, msg = False, f"Internal error: {e}"
        #schedule UI update back on main Kivy thread
        Clock.schedule_once(lambda dt: self._on_send_result(ok, msg, popup), 0)

    def _on_send_result(self, ok: bool, msg: str, popup: Popup):
        popup.dismiss()
        if ok:
            self._show_message("Recovery email sent", f"A recovery email was sent to {msg if isinstance(msg, str) else 'your email'}.")
        else:
            #msg should include error details from mp.sendRecoveryEmail
            self._show_message("Send failed", f"Failed to send recovery email: {msg}")

    def _show_message(self, title: str, message: str):
        box = BoxLayout(orientation="vertical", padding=10)
        box.add_widget(Label(text=message))
        btn = Button(text="OK", size_hint=(1, 0.25))
        p = Popup(title=title, content=box, size_hint=(0.8, 0.4))
        btn.bind(on_release=lambda *_: p.dismiss())
        box.add_widget(btn)
        p.open()
