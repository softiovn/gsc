import os
import sys
from PySide6.QtCore import QObject, pyqtSignal
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials


def resource_path(relative_path: str) -> str:
    """Get absolute path to resource (works for PyInstaller onefile build)."""
    try:
        base_path = sys._MEIPASS  # PyInstaller temp dir
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


class AuthManager(QObject):
    # ✅ Define PyQt signals
    authenticated = pyqtSignal(object)
    error_occurred = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.credentials_path = resource_path("config/credentials.json")
        self.token_path = resource_path("config/token.json")
        self.scopes = ["https://www.googleapis.com/auth/webmasters.readonly"]
        self.creds = None

    def authenticate(self):
        """Perform Google OAuth authentication."""
        try:
            if os.path.exists(self.token_path):
                self.creds = Credentials.from_authorized_user_file(
                    self.token_path, self.scopes
                )

            if not self.creds or not self.creds.valid:
                if self.creds and self.creds.expired and self.creds.refresh_token:
                    self.creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_path, self.scopes
                    )
                    self.creds = flow.run_local_server(port=0)

                # Save token for reuse
                with open(self.token_path, "w") as token:
                    token.write(self.creds.to_json())

            # ✅ Emit signal when authentication succeeds
            self.authenticated.emit(self.creds)

        except Exception as e:
            error_msg = f"Authentication failed: {e}"
            print("❌", error_msg)
            # ✅ Emit error signal
            self.error_occurred.emit(error_msg)

    def get_credentials(self):
        """Return current credentials."""
        return self.creds


# ===== Test run (standalone debug mode) =====
if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)

    def on_auth_success(creds):
        print("✅ Auth success. Token:", creds.token[:20] + "...")

    def on_auth_error(msg):
        print("❌ Error:", msg)

    auth = AuthManager()
    auth.authenticated.connect(on_auth_success)
    auth.error_occurred.connect(on_auth_error)
    auth.authenticate()

    sys.exit(app.exec_())
