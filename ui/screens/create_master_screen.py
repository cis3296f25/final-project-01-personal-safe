from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty, StringProperty
from kivy.logger import Logger
from core import masterPassword as mp
from core.vault import Vault
from app_state import app_state


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
            Logger.info("CreateMaster: master password created, switching screen")
            if "HOME" in self.manager.screen_names:
                self.manager.current = "HOME"
            else:
                self.manager.current = "LOGIN"
        except Exception as e:
            Logger.exception("Create master failed")
            self.error_text = f"Error: {e}"

    def goto_home(self):
        if "HOME" in self.manager.screen_names:
            self.manager.current = "HOME"
