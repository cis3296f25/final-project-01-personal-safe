from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty, StringProperty
from kivy.logger import Logger
from core import masterPassword as mp
from core.vault import Vault
from app_state import app_state
from kivy.clock import Clock
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput


class CreateMasterScreen(Screen):
    pwd1_field = ObjectProperty(None)
    pwd2_field = ObjectProperty(None)
    error_text = StringProperty("")

    def on_pre_enter(self, *args):
        self.error_text = ""
        if self.pwd1_field:
            self.pwd1_field.text = ""
        if self.pwd2_field:
            self.pwd2_field.text = ""

    def _validate(self, p1: str, p2: str) -> str | None:
        if not p1 or not p2:
            return "Both fields required"
        if p1.strip() != p1:
            return "No leading/trailing spaces"
        if len(p1) < 8:
            return "Use at least 8 characters"
        if p1 != p2:
            return "Passwords do not match"
        return None

    def do_create(self):
        p1 = (self.pwd1_field.text or "") if self.pwd1_field else ""
        p2 = (self.pwd2_field.text or "") if self.pwd2_field else ""
        err = self._validate(p1, p2)
        if err:
            self.error_text = err
            return
        try:
            Logger.info("CreateMaster: creating master password")
            mp.createMasterPassword(p1)
            app_state.vault = Vault(p1)
            app_state.master_password = p1
            Logger.info("CreateMaster: master password created")
            
            popup = RecoveryEmailPopup()
            popup.bind(on_dismiss=lambda *_: self._after_recovery_popup())
            popup.open()

        except Exception as e:
            Logger.exception("Create master failed")
            self.error_text = f"Error: {e}"

    def goto_home(self):
        if "HOME" in self.manager.screen_names:
            self.manager.current = "HOME"

    def _after_recovery_popup(self):
        self.error_text = ""
        if "HOME" in self.manager.screen_names:
            self.manager.current = "HOME"
        else:
            self.manager.current = "LOGIN"

    def saveRecoveryEmail(self, email_text: str):
        """Called from the KV popup 'Save' button via app.root.current_screen.save_recovery_email(...)"""
        email = (email_text or "").strip()
        if email:
            if "@" not in email or "." not in email:
                self.error_text = "Please enter a valid email address"
                return
        try:
            mp.setRecoveryEmail(email)
            self._show_info("Saved", f"Recovery email saved: {email or '(cleared)'}")
        except Exception as e:
            Logger.exception("save_recovery_email failed")
            self._show_info("Error", f"Failed to save recovery email: {e}")

    def _show_info(self, title: str, message: str):
        box = BoxLayout(orientation="vertical", padding=10, spacing=10)
        box.add_widget(Label(text=message))
        btn = Button(text="OK", size_hint=(1, 0.25))
        box.add_widget(btn)
        p = Popup(title=title, content=box, size_hint=(0.8, 0.4))
        btn.bind(on_release=lambda *_: p.dismiss())
        p.open()