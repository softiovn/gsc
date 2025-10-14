import os
import json
from PyQt5.QtCore import QObject, pyqtSignal
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

class AuthManager(QObject):
    authenticated = pyqtSignal(bool)
    error_occurred = pyqtSignal(str)
    
    # Google Search Console API scope
    SCOPES = ['https://www.googleapis.com/auth/webmasters.readonly']
    
    def __init__(self):
        super().__init__()
        self.credentials = None
        self.token_file = 'config/token.json'
        self.credentials_file = 'config/credentials.json'
        
    def authenticate(self):
        """Authenticate with Google APIs"""
        try:
            self.credentials = None
            
            # Token file stores user's access and refresh tokens
            if os.path.exists(self.token_file):
                self.credentials = Credentials.from_authorized_user_file(
                    self.token_file, self.SCOPES
                )
            
            # If there are no valid credentials, let the user log in
            if not self.credentials or not self.credentials.valid:
                if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                    self.credentials.refresh(Request())
                else:
                    if not os.path.exists(self.credentials_file):
                        self.error_occurred.emit(
                            "Credentials file not found. Please download from Google Cloud Console."
                        )
                        return
                    
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_file, self.SCOPES
                    )
                    self.credentials = flow.run_local_server(port=0)
                
                # Save credentials for next run
                os.makedirs(os.path.dirname(self.token_file), exist_ok=True)
                with open(self.token_file, 'w') as token:
                    token.write(self.credentials.to_json())
            
            self.authenticated.emit(True)
            
        except Exception as e:
            self.error_occurred.emit(f"Authentication failed: {str(e)}")
            self.authenticated.emit(False)
    
    def get_credentials(self):
        return self.credentials
    
    def is_authenticated(self):
        return self.credentials is not None and self.credentials.valid