class AppState:
    def __init__(self):
        self.vault = None
        self.master_password = ""


app_state = AppState()

app_state.smtp_config = {
    "host": "smtp.example.com",
    "port": 465,
    "username": "no-reply@example.com",
    "password": "secret",   # store securely in real app
    "use_ssl": True
}
