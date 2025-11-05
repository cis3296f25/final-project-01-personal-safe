from pathlib import Path
from typing import List, Tuple

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.core.clipboard import Clipboard
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.metrics import dp

import masterPassword as mp
from vault import Vault

# Load KV file if present
KV_PATH = Path(__file__).with_name("kivy_ui.kv")
if KV_PATH.exists():
    Builder.load_file(str(KV_PATH))


class LoginScreen(Screen):
    attempts = 3

    def on_pre_enter(self, *args):
        self.ids.password.text = ""
        self.ids.info.text = "Enter master password"

    def do_unlock(self):
        pw = self.ids.password.text
        if not pw:
            self.ids.info.text = "Password required"
            return
        if mp.verifyMasterPassword(pw):
            self.manager.app.set_master_and_open_home(pw)
            return
        self.attempts -= 1
        if self.attempts <= 0:
            self.ids.info.text = "Access denied"
            Clock.schedule_once(lambda *_: App.get_running_app().stop(), 0.6)
        else:
            self.ids.info.text = f"Incorrect. Attempts left: {self.attempts}"


class CreateMasterScreen(Screen):
    def on_pre_enter(self, *args):
        self.ids.new_pw.text = ""
        self.ids.confirm_pw.text = ""
        self.ids.info.text = "Create a new master password"

    def do_create(self):
        pw = self.ids.new_pw.text
        cf = self.ids.confirm_pw.text
        if not pw or not cf:
            self.ids.info.text = "Both fields required"
            return
        if pw.strip() != pw:
            self.ids.info.text = "No leading/trailing spaces"
            return
        if pw != cf:
            self.ids.info.text = "Passwords do not match"
            return
        mp.createMasterPassword(pw)
        self.manager.app.set_master_and_open_home(pw)


class HomeScreen(Screen):
    def on_pre_enter(self, *args):
        self.ids.status.text = "Ready"


class PersonalSafeApp(App):
    title = "Personal Safe (Kivy)"

    def build(self):
        Window.minimum_width, Window.minimum_height = 480, 380
        sm = ScreenManager(transition=FadeTransition())
        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(CreateMasterScreen(name="create"))
        sm.add_widget(HomeScreen(name="home"))
        sm.app = self
        self.sm = sm
        # Route based on existence of master hash
        if Path(mp.masterHashFile).exists():
            sm.current = "login"
        else:
            sm.current = "create"
        return sm

    def set_master_and_open_home(self, master_password: str):
        self.master_password = master_password
        self.vault = Vault(master_password)
        self.sm.current = "home"

    # UI actions bound from KV
    def action_add(self):
        self._open_add_popup()

    def action_view(self):
        self._open_view_popup()

    def action_delete(self):
        self._open_delete_popup()

    def _set_status(self, text: str):
        try:
            self.sm.get_screen("home").ids.status.text = text
        except Exception:
            pass

    # Popups
    def _open_add_popup(self):
        box = BoxLayout(orientation="vertical", padding=12, spacing=8)
        form = GridLayout(cols=2, spacing=8, size_hint_y=None, padding=(0, 0))
        # Ensure rows have a fixed height so children don't collapse/overlap
        form.row_force_default = True
        form.row_default_height = dp(40)
        form.bind(minimum_height=form.setter("height"))

        lbl_site = Label(
            text="Site", size_hint_y=None, height=dp(40), halign="left", valign="middle"
        )
        lbl_site.bind(size=lambda inst, *_: setattr(inst, "text_size", inst.size))
        form.add_widget(lbl_site)
        site_input = TextInput(multiline=False, size_hint_y=None, height=dp(40))
        form.add_widget(site_input)

        lbl_pwd = Label(
            text="Password",
            size_hint_y=None,
            height=dp(40),
            halign="left",
            valign="middle",
        )
        lbl_pwd.bind(size=lambda inst, *_: setattr(inst, "text_size", inst.size))
        form.add_widget(lbl_pwd)
        pwd_input = TextInput(
            password=True, multiline=False, size_hint_y=None, height=dp(40)
        )
        form.add_widget(pwd_input)

        box.add_widget(form)
        info = Label(text="", size_hint_y=None, height=dp(20))
        box.add_widget(info)
        btns = BoxLayout(size_hint_y=None, height=dp(48), spacing=8)
        btn_save = Button(text="Save")
        btn_cancel = Button(text="Cancel")
        btns.add_widget(btn_save)
        btns.add_widget(btn_cancel)
        box.add_widget(btns)
        popup = Popup(
            title="Add Password",
            content=box,
            size_hint=(None, None),
            size=(420, 260),
            auto_dismiss=False,
        )

        def do_save(*_):
            site = site_input.text.strip()
            pwd = pwd_input.text
            if not site or not pwd:
                info.text = "Site and password required"
                return
            self.vault.add(site, pwd)
            self._set_status(f"Saved {site}")
            popup.dismiss()

        btn_save.bind(on_release=do_save)
        btn_cancel.bind(on_release=lambda *_: popup.dismiss())
        popup.open()

    def _open_view_popup(self):
        # Build a scrollable list of passwords with reveal/copy
        root = BoxLayout(orientation="vertical", padding=12, spacing=8)
        scroll = ScrollView()
        list_box = GridLayout(cols=1, spacing=6, size_hint_y=None)
        list_box.bind(minimum_height=list_box.setter("height"))
        items: List[Tuple[str, str]] = self.vault.items()

        for site, pwd in items:
            row = BoxLayout(
                orientation="horizontal", size_hint_y=None, height=36, spacing=8
            )
            lbl_site = Label(
                text=site, size_hint_x=0.35, halign="left", valign="middle"
            )
            lbl_site.bind(size=lambda inst, *_: setattr(inst, "text_size", inst.size))
            masked = True
            lbl_pwd = Label(
                text="*" * min(12, len(pwd)),
                size_hint_x=0.35,
                halign="left",
                valign="middle",
            )
            lbl_pwd.bind(size=lambda inst, *_: setattr(inst, "text_size", inst.size))
            btn_reveal = Button(text="Reveal", size_hint_x=0.15)
            btn_copy = Button(text="Copy", size_hint_x=0.15)

            def make_toggle(label=lbl_pwd, p=pwd, b=btn_reveal):
                def _toggle(*_):
                    if label.text.startswith("*"):
                        label.text = p
                        b.text = "Hide"
                    else:
                        label.text = "*" * min(12, len(p))
                        b.text = "Reveal"

                return _toggle

            def make_copy(p=pwd):
                def _copy(*_):
                    Clipboard.copy(p)
                    self._set_status("Password copied")

                return _copy

            btn_reveal.bind(on_release=make_toggle())
            btn_copy.bind(on_release=make_copy())

            row.add_widget(lbl_site)
            row.add_widget(lbl_pwd)
            row.add_widget(btn_reveal)
            row.add_widget(btn_copy)
            list_box.add_widget(row)

        scroll.add_widget(list_box)
        root.add_widget(scroll)
        btn_close = Button(text="Close", size_hint_y=None, height=48)
        root.add_widget(btn_close)
        popup = Popup(
            title="View Passwords",
            content=root,
            size_hint=(0.9, 0.9),
            auto_dismiss=False,
        )
        btn_close.bind(on_release=lambda *_: popup.dismiss())
        popup.open()

    def _open_delete_popup(self):
        sites = self.vault.get_sites()
        if not sites:
            self._set_status("Vault is empty")
            return
        root = BoxLayout(orientation="vertical", padding=12, spacing=8)
        spinner = Spinner(text=sites[0], values=sites, size_hint_y=None, height=44)
        root.add_widget(Label(text="Select site to delete:"))
        root.add_widget(spinner)
        btns = BoxLayout(size_hint_y=None, height=48, spacing=8)
        btn_delete = Button(text="Delete")
        btn_cancel = Button(text="Cancel")
        btns.add_widget(btn_delete)
        btns.add_widget(btn_cancel)
        root.add_widget(btns)
        popup = Popup(
            title="Delete Entry",
            content=root,
            size_hint=(None, None),
            size=(380, 200),
            auto_dismiss=False,
        )

        def do_delete(*_):
            site = spinner.text
            if self.vault.delete(site):
                self._set_status(f"Deleted {site}")
                popup.dismiss()
            else:
                self._set_status("Entry not found")
                popup.dismiss()

        btn_delete.bind(on_release=do_delete)
        btn_cancel.bind(on_release=lambda *_: popup.dismiss())
        popup.open()


if __name__ == "__main__":
    PersonalSafeApp().run()
