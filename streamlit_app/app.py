import streamlit as st
from components.auth import AuthManager
from components.gmail_setup import GmailAuthManager
from components.user_config import UserConfig

# Page config
st.set_page_config(
    page_title="📧 Email Automation Bot",
    page_icon="📧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize auth
auth = AuthManager()


def main():
    """Main application flow."""
    if not auth.is_authenticated():
        show_login_page()
    else:
        show_dashboard()


def show_login_page():
    """Display login/signup page."""
    st.title("📧 Welcome to Email Automation Bot")
    st.write("AI-powered email management with intelligent draft generation")
    
    tab1, tab2 = st.tabs(["🔑 Login", "📝 Sign Up"])
    
    with tab1:
        st.subheader("Login to your account")
        
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login", width='stretch')
            
            if submit:
                success, message = auth.login_user(username, password)
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
    
    with tab2:
        st.subheader("Create a new account")
        
        with st.form("signup_form"):
            username = st.text_input("Username", key="signup_username")
            email = st.text_input("Email", key="signup_email")
            password = st.text_input("Password", type="password", key="signup_password")
            password_confirm = st.text_input("Confirm Password", type="password")
            submit = st.form_submit_button("Sign Up", width='stretch')
            
            if submit:
                if password != password_confirm:
                    st.error("Passwords do not match")
                else:
                    success, message = auth.register_user(username, email, password)
                    if success:
                        st.success(f"{message}. Please login.")
                    else:
                        st.error(message)


def show_dashboard():
    """Display main dashboard."""
    username = auth.get_current_user()
    
    # Sidebar
    st.sidebar.title(f"👤 {username}")
    st.sidebar.caption(st.session_state.get('email', ''))
    st.sidebar.markdown("---")
    
    if st.sidebar.button("🚪 Logout", width='stretch'):
        auth.logout_user()
        st.rerun()
    
    # Check setup status
    gmail_auth = GmailAuthManager(username)
    config = UserConfig(username)
    
    gmail_connected = gmail_auth.is_authenticated()
    api_key_set = bool(config.get_groq_key())
    
    if not gmail_connected or not api_key_set:
        show_setup_wizard(gmail_connected, api_key_set)
    else:
        show_main_app()


def show_setup_wizard(gmail_connected, api_key_set):
    """Guide user through setup."""
    st.title("🚀 Let's Get Started!")
    st.write("Complete these steps to start automating your emails")
    st.markdown("---")
    
    username = auth.get_current_user()
    gmail_auth = GmailAuthManager(username)
    config = UserConfig(username)
    
    # Step 1: Gmail Connection
    with st.expander("📧 Step 1: Connect Gmail", expanded=not gmail_connected):
        if gmail_connected:
            st.success("✅ Gmail is connected!")
            if st.button("🔓 Disconnect Gmail"):
                if gmail_auth.revoke_access():
                    st.success("Gmail disconnected")
                    st.rerun()
        else:
            st.info("We need access to your Gmail to read emails and create drafts.")
            
            auth_url = gmail_auth.get_auth_url()
            
            if auth_url:
                st.markdown(f"**Step 1:** [Click here to authorize Gmail]({auth_url})")
                st.markdown("**Step 2:** Copy the authorization code and paste it below")
                
                code = st.text_input("Authorization Code:", key="gmail_auth_code")
                
                if st.button("Connect Gmail", type="primary"):
                    if code:
                        success, message = gmail_auth.handle_oauth_callback(code)
                        if success:
                            st.success(message)
                            st.balloons()
                            st.rerun()
                        else:
                            st.error(message)
                    else:
                        st.warning("Please enter the authorization code")
    
    # Step 2: API Key
    with st.expander("🔑 Step 2: Add Groq API Key", expanded=gmail_connected and not api_key_set):
        if api_key_set:
            st.success("✅ API key is configured!")
            if st.checkbox("Show API Key"):
                st.code(config.get_groq_key())
        else:
            st.info("Get your free API key from [console.groq.com](https://console.groq.com)")
            
            api_key = st.text_input("Enter your Groq API Key:", type="password", key="groq_api_key")
            
            if st.button("💾 Save API Key", type="primary"):
                if api_key:
                    if config.set_groq_key(api_key):
                        st.success("API key saved successfully!")
                        st.rerun()
                else:
                    st.warning("Please enter your API key")
    
    # Completion
    st.markdown("---")
    if gmail_connected and api_key_set:
        st.success("🎉 Setup complete! You're ready to process emails.")
        if st.button("Go to Dashboard →", type="primary", width='stretch'):
            st.rerun()


def show_main_app():
    """Main application interface."""
    st.title("📧 Email Automation Dashboard")
    
    st.success("✨ Your account is fully configured!")
    
    st.markdown("### Quick Navigation")
    st.info("Use the sidebar to navigate between pages:")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### 🏠 Dashboard")
        st.write("Process emails and review drafts")
    
    with col2:
        st.markdown("#### ⚙️ Settings")
        st.write("Configure preferences and API keys")
    
    with col3:
        st.markdown("#### 📊 History")
        st.write("View your activity logs")
    
    st.markdown("---")
    st.info("👈 Click on a page in the sidebar to get started!")


if __name__ == "__main__":
    main()