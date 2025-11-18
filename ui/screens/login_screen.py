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
import os
import json
import re

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

    def _send_recovery_thread(self, email, smtp_config, popup):
        try:
            if smtp_config is None:
                import secrets
                token = secrets.token_urlsafe(32)
                mp.storeTokenHash(token, ttl_seconds=3600)
                Clock.schedule_once(lambda dt: self._on_send_result(True, f"DEV TOKEN: {token}", popup), 0)
                return

            ok, msg = mp.generate_and_send_recovery(smtp_config, email, ttl_seconds=3600)
            Clock.schedule_once(lambda dt: self._on_send_result(ok, msg, popup), 0)
        except Exception as e:
            Logger.exception("forgot_password: unexpected error")
            Clock.schedule_once(lambda dt: self._on_send_result(False, f"Internal error: {e}", popup), 0)

    def _on_send_result(self, ok: bool, msg: str, popup: Popup):
        popup.dismiss()
        self._forgot_sending = False
        if ok:
            if msg.startswith("DEV TOKEN:"):
                token = msg.split("DEV TOKEN: ", 1)[-1]
                self._show_popup("Dev token (testing only)", f"Use this token to reset: {token}")
            else:
                self._show_popup("Recovery email sent", f"A recovery email was sent to {msg if isinstance(msg, str) else 'your email'}.")
        else:
            self._show_popup("Send failed", f"Failed to send recovery email: {msg}")

    def _show_popup(self, title: str, message: str):
        content = BoxLayout(orientation="vertical", padding=12, spacing=12)
        content.add_widget(Label(text=message))
        btn = Button(text="OK", size_hint_y=None, height="40dp")
        content.add_widget(btn)
        popup = Popup(title=title, content=content, size_hint=(None, None), size=(420, 220))
        btn.bind(on_release=popup.dismiss)
        popup.open()

    def _load_profile_file(self) -> dict:
        """Try to load profile JSON from app user_data_dir then fallback to local file."""
        try:
            user_dir = App.get_running_app().user_data_dir
        except Exception:
            user_dir = None

        candidates = []
        if user_dir:
            candidates.append(os.path.join(user_dir, "user_profile.json"))
        candidates.append("user_profile.json")

        for p in candidates:
            if os.path.exists(p):
                try:
                    with open(p, "r", encoding="utf-8") as f:
                        return json.load(f) or {}
                except Exception:
                    Logger.exception(f"Failed to read profile file: {p}")
        return {}

    def forgot_password(self):
        Logger.info("LoginScreen: forgot_password called")

        # 1) Check app_state.profile
        Logger.info(f"LoginScreen: app_state.profile = {getattr(app_state, 'profile', None)!r}")

        # 2) Check user_data_dir path and whether the file exists there
        try:
            user_dir = App.get_running_app().user_data_dir
        except Exception:
            user_dir = None
        Logger.info(f"LoginScreen: app user_data_dir = {user_dir!r}")
        # 3) Check both candidate file paths
        candidates = []
        if user_dir:
            candidates.append(os.path.join(user_dir, "user_profile.json"))
        candidates.append("user_profile.json")
        for p in candidates:
            Logger.info(f"LoginScreen: checking profile file: {p} -> exists={os.path.exists(p)}")
        """Handle forgot password flow: get recovery email, validate, and notify user (simulated)."""
        Logger.info("LoginScreen: forgot_password called")

        # Preferred: app_state.profile (set by ProfileScreen.save_profile)
        profile = getattr(app_state, "profile", None) or {}
        if not profile:
            profile = self._load_profile_file()

        email = ""
        if isinstance(profile, dict):
            email = profile.get("email", "") or ""
        else:
            # defensive: if app_state.profile is a string or other, safely coerce
            try:
                email = str(profile)
            except Exception:
                email = ""

        if not email:
            self._show_popup(
                "No recovery email",
                "No recovery email configured. Go to Profile and set one."
            )
            return

        # Basic validation
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            self._show_popup(
                "Invalid email",
                "The configured recovery email looks invalid. Please update it in Profile."
            )
            return

        # Simulate sending recovery email (replace with real email-sending logic if available)
        Logger.info(f"LoginScreen: sending recovery (simulated) to {email}")
        self._show_popup(
            "Recovery sent",
            f"A recovery link has been sent to {email} (simulated)."
        )
