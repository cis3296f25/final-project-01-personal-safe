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
            mp.createMasterPassword(p1)
            app_state.vault = Vault(p1)
            app_state.master_password = p1
            if "HOME" in self.manager.screen_names:
                self.manager.current = "HOME"
            else:
                self.manager.current = "LOGIN"
        except Exception as e:
            Logger.exception("Create master failed")
            self.error_text = f"Error: {e}"


from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty, StringProperty
from kivy.logger import Logger


# Optional: inject a service (e.g., vault_service) from the App
def _service(app):
    return getattr(app, "vault_service", None)


class CreateMasterScreen(Screen):
    error_text = StringProperty("")  # Bound to error label
    pwd1_field = ObjectProperty(None)  # Bound to first password TextInput
    pwd2_field = ObjectProperty(None)  # Bound to confirm TextInput

    def on_pre_enter(self, *args):
        # Reset UI state
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
        p1 = self.pwd1_field.text if self.pwd1_field else ""
        p2 = self.pwd2_field.text if self.pwd2_field else ""
        error = self._validate(p1, p2)
        if error:
            self.error_text = error
            return

        app = self.get_app()
        svc = _service(app)
        try:
            # Your existing master password creation logic
            (
                app.create_master_password(p1)
                if hasattr(app, "create_master_password")
                else Logger.warning("App missing create_master_password")
            )
            # Or via service: svc.create_master(p1)
            if hasattr(app, "set_master_and_open_home"):
                app.set_master_and_open_home(p1)
            else:
                Logger.warning("App missing set_master_and_open_home")
        except Exception as e:
            Logger.exception("Failed to create master")
            self.error_text = f"Error: {e}"

    def get_app(self):
        # Safer than importing App globally
        from kivy.app import App

        return App.get_running_app()
