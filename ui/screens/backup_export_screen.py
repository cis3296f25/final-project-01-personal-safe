from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty, ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.button import Button
from app_state import app_state
from kivy.logger import Logger


class BackupExportScreen(Screen):
    info_text = StringProperty("")
    path_field = ObjectProperty(None)

    def on_pre_enter(self, *args):
        self.info_text = ""
        if self.path_field:
            # default filename in current dir
            self.path_field.text = "vault_backup.psafe"

    def do_export(self):
        vault = getattr(app_state, "vault", None)
        if not vault:
            self._show_popup("No vault", "Vault not loaded.")
            return

        # Prefer using current master in memory, otherwise ask
        master_pw = getattr(app_state, "master_password", "") or None
        filepath = (self.path_field.text or "").strip() if self.path_field else ""
        if not filepath:
            self._show_popup("Path required", "Enter a backup filepath.")
            return

        if not master_pw:
            # ask user for master password via popup
            self._ask_for_password_and_export(filepath)
            return

        try:
            vault.export_encrypted_backup(filepath, master_pw)
            self._show_popup("Export complete", f"Backup saved to: {filepath}")
            self.info_text = "Export successful"
        except Exception as e:
            Logger.exception("Export failed")
            self._show_popup("Export failed", f"Failed to export backup: {e}")
            self.info_text = f"Error: {e}"

    def _ask_for_password_and_export(self, filepath: str):
        content = BoxLayout(orientation="vertical", padding=8, spacing=8)
        pw_input = TextInput(password=True, multiline=False, hint_text="Master password")
        content.add_widget(Label(text="Enter master password to encrypt backup:"))
        content.add_widget(pw_input)
        btn_layout = BoxLayout(size_hint_y=None, height="40dp", spacing=8)
        ok = Button(text="Export")
        cancel = Button(text="Cancel")
        btn_layout.add_widget(ok)
        btn_layout.add_widget(cancel)
        content.add_widget(btn_layout)
        popup = Popup(title="Export Backup", content=content, size_hint=(None, None), size=(420, 220))
        cancel.bind(on_release=popup.dismiss)

        def _do(_: None):
            popup.dismiss()
            try:
                app_state.vault.export_encrypted_backup(filepath, pw_input.text or "")
                self._show_popup("Export complete", f"Backup saved to: {filepath}")
            except Exception as e:
                Logger.exception("Export failed with supplied password")
                self._show_popup("Export failed", f"Failed: {e}")

        ok.bind(on_release=_do)
        popup.open()

    def _show_popup(self, title: str, message: str):
        content = BoxLayout(orientation="vertical", padding=8, spacing=8)
        content.add_widget(Label(text=message))
        btn = Button(text="OK", size_hint_y=None, height="40dp")
        content.add_widget(btn)
        popup = Popup(title=title, content=content, size_hint=(None, None), size=(420, 160))
        btn.bind(on_release=popup.dismiss)
        popup.open()

    def goto_home(self):
        if "HOME" in self.manager.screen_names:
            self.manager.current = "HOME"