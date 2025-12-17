import streamlit as st
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from pathlib import Path


class GmailAuthManager:
    """Manages Gmail OAuth for users."""
    
    def __init__(self, username):
        self.username = username
        self.user_folder = Path(f"streamlit_app/data/users/{username}")
        self.user_folder.mkdir(parents=True, exist_ok=True)
        
        self.token_file = self.user_folder / "token.json"
        self.credentials_file = "config/credentials.json"
        self.scopes = ["https://mail.google.com/"]
    
    def is_authenticated(self) -> bool:
        """Check if user has valid Gmail token."""
        try:
            if not self.token_file.exists():
                return False
            
            creds = Credentials.from_authorized_user_file(
                str(self.token_file), self.scopes
            )
            
            if creds and creds.valid:
                return True
            
            # Try to refresh if expired
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                    self._save_token(creds)
                    return True
                except Exception:
                    return False
            
            return False
            
        except Exception as e:
            st.error(f"Error checking authentication: {e}")
            return False
    
    def get_auth_url(self) -> str:
        """Generate Gmail OAuth URL for user."""
        try:
            flow = InstalledAppFlow.from_client_secrets_file(
                self.credentials_file,
                scopes=self.scopes,
                redirect_uri='urn:ietf:wg:oauth:2.0:oob'
            )
            
            auth_url, _ = flow.authorization_url(
                access_type='offline',
                include_granted_scopes='true',
                prompt='consent'
            )
            
            # Store flow in session for later use
            st.session_state[f'gmail_flow_{self.username}'] = flow
            
            return auth_url
            
        except Exception as e:
            st.error(f"Error generating auth URL: {e}")
            return ""
    
    def handle_oauth_callback(self, code: str) -> tuple:
        """
        Handle OAuth callback and save token.
        Returns (success: bool, message: str)
        """
        try:
            if not code:
                return False, "Authorization code is required"
            
            # Get flow from session
            flow = st.session_state.get(f'gmail_flow_{self.username}')
            
            if not flow:
                # Recreate flow if not in session
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file,
                    scopes=self.scopes,
                    redirect_uri='urn:ietf:wg:oauth:2.0:oob'
                )
            
            # Exchange code for token
            flow.fetch_token(code=code.strip())
            creds = flow.credentials
            
            # Save token
            self._save_token(creds)
            
            # Clean up session
            st.session_state.pop(f'gmail_flow_{self.username}', None)
            
            return True, "Gmail connected successfully"
            
        except Exception as e:
            return False, f"OAuth failed: {str(e)}"
    
    def get_gmail_service(self):
        """Get authenticated Gmail service."""
        try:
            if not self.token_file.exists():
                raise Exception("User is not authenticated with Gmail")
            
            creds = Credentials.from_authorized_user_file(
                str(self.token_file), self.scopes
            )
            
            # Refresh if expired
            if creds.expired and creds.refresh_token:
                creds.refresh(Request())
                self._save_token(creds)
            
            return build("gmail", "v1", credentials=creds)
            
        except Exception as e:
            st.error(f"Error getting Gmail service: {e}")
            raise
    
    def revoke_access(self):
        """Revoke Gmail access."""
        try:
            if self.token_file.exists():
                self.token_file.unlink()
                return True
        except Exception as e:
            st.error(f"Error revoking access: {e}")
            return False
    
    def _save_token(self, creds: Credentials):
        """Save credentials to token.json."""
        try:
            with open(self.token_file, "w") as token:
                token.write(creds.to_json())
        except Exception as e:
            st.error(f"Error saving token: {e}")
