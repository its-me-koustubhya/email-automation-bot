import streamlit as st
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

from streamlit_app.components.auth import AuthManager
from streamlit_app.components.gmail_setup import GmailAuthManager
from streamlit_app.components.user_config import UserConfig

st.set_page_config(page_title="Settings", page_icon="⚙️")

# Check authentication
auth = AuthManager()
if not auth.is_authenticated():
    st.warning("⚠️ Please login first")
    st.stop()

st.title("⚙️ Settings")

username = auth.get_current_user()
config = UserConfig(username)
gmail_auth = GmailAuthManager(username)

# API Key Section
st.subheader("🔑 Groq API Key")

current_key = config.get_groq_key()

if current_key:
    st.success("✅ API key is configured")
    show_key = st.checkbox("Show API key")
    
    if show_key:
        st.code(current_key)
else:
    st.warning("⚠️ No API key configured")
    st.info("Get your free API key from [console.groq.com](https://console.groq.com)")

with st.form("api_key_form"):
    new_key = st.text_input("Groq API Key:", type="password", value=current_key if current_key else "")
    submit = st.form_submit_button("💾 Save API Key", width='stretch')
    
    if submit:
        if new_key:
            if config.set_groq_key(new_key):
                st.success("✅ API key saved successfully!")
                st.rerun()
        else:
            st.warning("Please enter an API key")

st.markdown("---")

# Gmail Connection
st.subheader("📧 Gmail Connection")

if gmail_auth.is_authenticated():
    st.success("✅ Gmail is connected")
    st.info("Your Gmail account is properly authenticated")
    
    if st.button("🔓 Disconnect Gmail", type="secondary"):
        if gmail_auth.revoke_access():
            st.success("Gmail disconnected successfully")
            st.rerun()
else:
    st.warning("⚠️ Gmail is not connected")
    st.info("Go to the main page to connect your Gmail account")

st.markdown("---")

# Processing Settings
st.subheader("⚙️ Email Processing Settings")

settings = config.get_settings()

with st.form("settings_form"):
    max_emails = st.slider(
        "Maximum emails to process per run:",
        min_value=1,
        max_value=50,
        value=settings.get('max_emails', 10),
        help="Limit the number of emails to process in one run"
    )
    
    categories = st.multiselect(
        "Email categories to process:",
        options=["primary", "social", "promotions", "updates"],
        default=settings.get('categories', ['primary']),
        help="Select which Gmail categories to include"
    )
    
    auto_mark_read = st.checkbox(
        "Automatically mark processed emails as read",
        value=settings.get('auto_mark_read', True),
        help="Mark emails as read after processing"
    )
    
    submit = st.form_submit_button("💾 Save Settings", width='stretch')
    
    if submit:
        updated_settings = {
            'max_emails': max_emails,
            'categories': categories,
            'auto_mark_read': auto_mark_read
        }
        
        if config.update_settings(updated_settings):
            st.success("✅ Settings saved successfully!")
            st.rerun()

st.markdown("---")

# Account Info
st.subheader("👤 Account Information")

st.write(f"**Username:** {username}")
st.write(f"**Email:** {st.session_state.get('email', 'N/A')}")

st.caption("Need to change account settings? Contact support.")