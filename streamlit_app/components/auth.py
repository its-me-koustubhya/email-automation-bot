import streamlit as st
import yaml
import bcrypt
from pathlib import Path
from datetime import datetime
import json


class AuthManager:
    """Manages user authentication and session."""
    
    def __init__(self):
        self.users_file = Path("streamlit_app/data/users.yaml")
        self.ensure_users_file()
    
    def ensure_users_file(self):
        """Create users file and directory if it doesn't exist."""
        try:
            self.users_file.parent.mkdir(parents=True, exist_ok=True)
            
            if not self.users_file.exists():
                initial_data = {
                    "credentials": {
                        "usernames": {}
                    }
                }
                with open(self.users_file, "w") as f:
                    yaml.safe_dump(initial_data, f)
        except Exception as e:
            st.error(f"Error creating users file: {e}")
    
    def load_users(self):
        """Load users from YAML file."""
        try:
            with open(self.users_file, "r") as f:
                return yaml.safe_load(f)
        except Exception as e:
            st.error(f"Error loading users: {e}")
            return {"credentials": {"usernames": {}}}
    
    def save_users(self, users):
        """Save users to YAML file."""
        try:
            with open(self.users_file, "w") as f:
                yaml.safe_dump(users, f)
        except Exception as e:
            st.error(f"Error saving users: {e}")
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt."""
        try:
            hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
            return hashed.decode("utf-8")
        except Exception as e:
            st.error(f"Error hashing password: {e}")
            return ""
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash."""
        try:
            return bcrypt.checkpw(
                password.encode("utf-8"),
                hashed.encode("utf-8")
            )
        except Exception as e:
            st.error(f"Error verifying password: {e}")
            return False
    
    def create_user_folder(self, username: str):
        """Create user-specific folder and config."""
        try:
            user_dir = Path(f"streamlit_app/data/users/{username}")
            user_dir.mkdir(parents=True, exist_ok=True)
            
            # Create initial config
            config = {
                "groq_api_key": "",
                "gmail_authenticated": False,
                "settings": {
                    "max_emails": 10,
                    "categories": ["primary"],
                    "auto_mark_read": True
                }
            }
            
            config_file = user_dir / "config.json"
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
            
            # Create empty history file
            history_file = user_dir / "history.json"
            with open(history_file, 'w') as f:
                json.dump([], f)
                
        except Exception as e:
            st.error(f"Error creating user folder: {e}")
    
    def register_user(self, username: str, email: str, password: str) -> tuple:
        """
        Register a new user.
        Returns (success: bool, message: str)
        """
        try:
            if not username or not email or not password:
                return False, "All fields are required"
            
            if len(password) < 6:
                return False, "Password must be at least 6 characters"
            
            users = self.load_users()
            usernames = users["credentials"]["usernames"]
            
            if username in usernames:
                return False, "Username already exists"
            
            # Check if email already exists
            for user_data in usernames.values():
                if user_data.get("email") == email:
                    return False, "Email already registered"
            
            usernames[username] = {
                "email": email,
                "name": username,
                "password": self.hash_password(password),
                "created_at": datetime.utcnow().isoformat()
            }
            
            self.save_users(users)
            self.create_user_folder(username)
            
            return True, "Account created successfully"
            
        except Exception as e:
            return False, f"Registration error: {str(e)}"
    
    def login_user(self, username: str, password: str) -> tuple:
        """
        Login user and create session.
        Returns (success: bool, message: str)
        """
        try:
            if not username or not password:
                return False, "Username and password required"
            
            users = self.load_users()
            usernames = users["credentials"]["usernames"]
            
            if username not in usernames:
                return False, "Invalid username or password"
            
            user = usernames[username]
            
            if not self.verify_password(password, user["password"]):
                return False, "Invalid username or password"
            
            # Set session state
            st.session_state["authenticated"] = True
            st.session_state["username"] = username
            st.session_state["email"] = user["email"]
            
            return True, "Login successful"
            
        except Exception as e:
            return False, f"Login error: {str(e)}"
    
    def logout_user(self):
        """Logout user and clear session."""
        try:
            keys_to_clear = ["authenticated", "username", "email"]
            for key in keys_to_clear:
                st.session_state.pop(key, None)
        except Exception as e:
            st.error(f"Logout error: {e}")
    
    def is_authenticated(self) -> bool:
        """Check if user is logged in."""
        return st.session_state.get("authenticated", False)
    
    def get_current_user(self):
        """Get current logged in user."""
        return st.session_state.get("username", None)