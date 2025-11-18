from kivy.uix.screenmanager import Screen
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from app_state import app_state

class VerifyCodeScreen(Screen):
    def verify_code(self, code_input):
        if code_input == getattr(app_state, 'reset_code', None):
            app_state.reset_code = None
            self.manager.current = "RESET_PASSWORD"
        else:
            self._show_popup("Invalid Code", "The code you entered is incorrect.")

    def _show_popup(self, title, message):
        content = BoxLayout(orientation="vertical", padding=12, spacing=12)
        content.add_widget(Label(text=message))
        btn = Button(text="OK", size_hint_y=None, height="40dp")
        content.add_widget(btn)
        popup = Popup(title=title, content=content, size_hint=(None, None), size=(420, 220))
        btn.bind(on_release=popup.dismiss)
        popup.open()