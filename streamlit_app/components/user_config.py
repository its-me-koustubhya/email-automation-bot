import json
from pathlib import Path
import streamlit as st


class UserConfig:
    """Manage user configuration."""
    
    def __init__(self, username):
        self.username = username
        self.user_folder = Path(f"streamlit_app/data/users/{username}")
        self.config_file = self.user_folder / "config.json"
        self.history_file = self.user_folder / "history.json"
    
    def load_config(self):
        """Load user config."""
        try:
            if not self.config_file.exists():
                return self._default_config()
            
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            st.error(f"Error loading config: {e}")
            return self._default_config()
    
    def save_config(self, config):
        """Save user config."""
        try:
            self.user_folder.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            st.error(f"Error saving config: {e}")
    
    def get_groq_key(self):
        """Get user's Groq API key."""
        config = self.load_config()
        return config.get('groq_api_key', '')
    
    def set_groq_key(self, api_key):
        """Save user's Groq API key."""
        try:
            config = self.load_config()
            config['groq_api_key'] = api_key
            self.save_config(config)
            return True
        except Exception as e:
            st.error(f"Error saving API key: {e}")
            return False
    
    def get_settings(self):
        """Get user settings."""
        config = self.load_config()
        return config.get('settings', self._default_config()['settings'])
    
    def update_settings(self, settings):
        """Update user settings."""
        try:
            config = self.load_config()
            config['settings'] = settings
            self.save_config(config)
            return True
        except Exception as e:
            st.error(f"Error updating settings: {e}")
            return False
    
    def add_history(self, entry):
        """Add entry to history."""
        try:
            history = self.load_history()
            history.append(entry)
            
            # Keep only last 100 entries
            if len(history) > 100:
                history = history[-100:]
            
            with open(self.history_file, 'w') as f:
                json.dump(history, f, indent=2)
        except Exception as e:
            st.error(f"Error saving history: {e}")
    
    def load_history(self):
        """Load user history."""
        try:
            if not self.history_file.exists():
                return []
            
            with open(self.history_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            st.error(f"Error loading history: {e}")
            return []
    
    def _default_config(self):
        """Default configuration."""
        return {
            "groq_api_key": "",
            "gmail_authenticated": False,
            "settings": {
                "max_emails": 10,
                "categories": ["primary"],
                "auto_mark_read": True
            }
        }
