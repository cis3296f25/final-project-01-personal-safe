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
            # ask for recovery email
            self._ask_and_save_recovery_email()

            if "HOME" in self.manager.screen_names:
                self.manager.current = "HOME"
            else:
                self.manager.current = "LOGIN"
        except Exception as e:
            Logger.exception("Create master failed")
            self.error_text = f"Error: {e}"

    def _ask_and_save_recovery_email(self):
        """Popup that asks for a recovery email and saves it via mp.setRecoveryEmail"""
        box = BoxLayout(orientation="vertical", spacing=8, padding=10)
        ti = TextInput(hint_text="Recovery email (optional)", multiline=False)
        box.add_widget(ti)
        btn_box = BoxLayout(size_hint_y=None, height="40dp", spacing=8)
        save_btn = Button(text="Save")
        cancel_btn = Button(text="Cancel")
        btn_box.add_widget(save_btn)
        btn_box.add_widget(cancel_btn)
        box.add_widget(btn_box)

        popup = Popup(title="Recovery email (optional)", content=box, size_hint=(0.8, 0.4))
        def on_save(*_):
            email = (ti.text or "").strip()
            if email:
                # very light validation — keep it simple
                if "@" not in email or "." not in email:
                    # inform user and don't close
                    self.error_text = "Please enter a valid email address"
                    return
                try:
                    mp.setRecoveryEmail(email)
                except Exception as e:
                    Logger.exception("setRecoveryEmail failed")
                    self.error_text = f"Failed to save recovery email: {e}"
                finally:
                    popup.dismiss()
            else:
                try:
                    mp.setRecoveryEmail("")
                except Exception:
                    pass
                popup.dismiss()

        def on_cancel(*_):
            popup.dismiss()

        save_btn.bind(on_release=on_save)
        cancel_btn.bind(on_release=on_cancel)
        popup.open()