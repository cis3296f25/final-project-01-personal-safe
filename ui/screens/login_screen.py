from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty, StringProperty
from kivy.logger import Logger

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
