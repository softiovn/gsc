import os
import json
from PyQt5.QtCore import QObject, pyqtSignal
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2 import service_account

class AuthManager(QObject):
    authenticated = pyqtSignal(bool)
    error_occurred = pyqtSignal(str)
    
    # Google Search Console API scope
    SCOPES = ['https://www.googleapis.com/auth/webmasters.readonly']
    
    def __init__(self):
        super().__init__()
        self.credentials = None
        self.token_file = 'config/token.json'
        
    def get_credentials_dict(self):
        """Replace with your actual Google Cloud credentials"""
        return {
            "installed": {
                "client_id": "736527399714-dsnqc8b8lbt88jpv8731q788r6qpr1i4.apps.googleusercontent.com",
                "project_id": "soft-io-vn",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_secret": "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",
                "redirect_uris": ["http://localhost"]
            }
        }
    
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
                    # Use embedded credentials instead of file
                    credentials_dict = self.get_credentials_dict()
                    
                    flow = InstalledAppFlow.from_client_config(
                        credentials_dict, 
                        self.SCOPES
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