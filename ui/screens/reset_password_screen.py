# ui/screens/reset_password_screen.py
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup

class ResetPasswordScreen(Screen):
    #def reset_password(self, new_password, confirm_password):

    def _show_popup(self, title, message):
        content = BoxLayout(orientation="vertical", padding=12, spacing=12)
        content.add_widget(Label(text=message))
        btn = Button(text="OK", size_hint_y=None, height="40dp")
        content.add_widget(btn)
        popup = Popup(title=title, content=content, size_hint=(None, None), size=(420, 220))
        btn.bind(on_release=popup.dismiss)
        popup.open()
