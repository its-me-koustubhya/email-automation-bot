import streamlit as st
import sys
from pathlib import Path
import os
from datetime import datetime

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from streamlit_app.components.auth import AuthManager
from streamlit_app.components.gmail_setup import GmailAuthManager
from streamlit_app.components.user_config import UserConfig
from tools.gmail_tools import fetch_unread_emails, create_draft, mark_as_read
from tools.llm_tools import analyze_email, generate_response

st.set_page_config(page_title="Dashboard", page_icon="🏠", layout="wide")

# Check authentication
auth = AuthManager()
if not auth.is_authenticated():
    st.warning("⚠️ Please login first")
    st.stop()

username = auth.get_current_user()
config = UserConfig(username)
gmail_auth = GmailAuthManager(username)

# Check setup
if not gmail_auth.is_authenticated():
    st.warning("⚠️ Please connect Gmail first (go to main page)")
    st.stop()

if not config.get_groq_key():
    st.warning("⚠️ Please add Groq API key in Settings")
    st.stop()

# Initialize session state
if 'metrics' not in st.session_state:
    st.session_state.metrics = {
        'processed': 0,
        'drafted': 0,
        'skipped': 0
    }

st.title("🏠 Email Processing Dashboard")

# Metrics
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("📧 Processed", st.session_state.metrics['processed'])
with col2:
    st.metric("📝 Drafted", st.session_state.metrics['drafted'])
with col3:
    st.metric("⏭️ Skipped", st.session_state.metrics['skipped'])

st.markdown("---")

# Settings
settings = config.get_settings()
max_emails = settings.get('max_emails', 10)

col1, col2 = st.columns([3, 1])
with col1:
    st.subheader("Process Unread Emails")
with col2:
    if st.button("🔄 Process Emails", type="primary", width='stretch'):
        st.session_state.process_clicked = True

if st.session_state.get('process_clicked', False):
    try:
        # Set API key
        os.environ['GROQ_API_KEY'] = config.get_groq_key()
        
        # Get Gmail service
        service = gmail_auth.get_gmail_service()
        
        # Fetch emails
        with st.spinner(f"Fetching up to {max_emails} unread emails..."):
            emails = fetch_unread_emails(
                service,
                max_results=max_emails,
                query='is:unread category:primary'
            )
        
        if not emails:
            st.info("📭 No unread emails found in primary inbox")
            st.session_state.process_clicked = False
            st.stop()
        
        st.success(f"✅ Found {len(emails)} unread emails")
        
        # Process each email
        drafted_count = 0
        skipped_count = 0
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for idx, email in enumerate(emails):
            progress = (idx + 1) / len(emails)
            progress_bar.progress(progress)
            status_text.text(f"Processing email {idx + 1}/{len(emails)}...")
            
            with st.expander(f"📨 {email['subject'][:60]}..."):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.write(f"**From:** {email['sender']}")
                    st.write(f"**Subject:** {email['subject']}")
                    
                with col2:
                    st.caption(f"ID: {email['id'][:8]}...")
                
                st.text_area("Email Preview:", email['body'][:300] + "...", height=100, disabled=True)
                
                # Analyze email
                with st.spinner("Analyzing..."):
                    analysis = analyze_email(email)
                
                col1, col2, col3 = st.columns(3)
                col1.metric("Category", analysis['category'])
                col2.metric("Urgency", analysis['urgency'])
                col3.metric("Respond?", "Yes" if analysis['should_respond'] else "No")
                
                if analysis['should_respond']:
                    # Generate response
                    with st.spinner("Generating response..."):
                        draft_text = generate_response(email, analysis)
                    
                    st.markdown("**Generated Draft:**")
                    st.text_area("", draft_text, height=200, disabled=True, key=f"draft_{email['id']}")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if st.button("✅ Create Draft", key=f"approve_{email['id']}", width='stretch'):
                            try:
                                create_draft(
                                    service,
                                    to=email['sender'],
                                    subject=f"Re: {email['subject']}",
                                    body=draft_text,
                                    thread_id=email['thread_id']
                                )
                                mark_as_read(service, email['id'])
                                
                                # Add to history
                                config.add_history({
                                    'timestamp': datetime.now().isoformat(),
                                    'action': 'draft_created',
                                    'email': email['subject'],
                                    'sender': email['sender']
                                })
                                
                                drafted_count += 1
                                st.success("✅ Draft created!")
                            except Exception as e:
                                st.error(f"Error creating draft: {e}")
                    
                    with col2:
                        if st.button("❌ Skip", key=f"skip_{email['id']}", width='stretch'):
                            try:
                                mark_as_read(service, email['id'])
                                
                                # Add to history
                                config.add_history({
                                    'timestamp': datetime.now().isoformat(),
                                    'action': 'skipped',
                                    'email': email['subject'],
                                    'sender': email['sender']
                                })
                                
                                skipped_count += 1
                                st.info("⏭️ Email skipped")
                            except Exception as e:
                                st.error(f"Error skipping: {e}")
                else:
                    st.info("⏭️ No response needed - marking as read")
                    try:
                        mark_as_read(service, email['id'])
                        
                        # Add to history
                        config.add_history({
                            'timestamp': datetime.now().isoformat(),
                            'action': 'auto_skipped',
                            'email': email['subject'],
                            'sender': email['sender']
                        })
                        
                        skipped_count += 1
                    except Exception as e:
                        st.error(f"Error: {e}")
        
        # Update metrics
        st.session_state.metrics['processed'] = len(emails)
        st.session_state.metrics['drafted'] = drafted_count
        st.session_state.metrics['skipped'] = skipped_count
        
        progress_bar.empty()
        status_text.empty()
        
        st.balloons()
        st.success(f"✅ Processed {len(emails)} emails! {drafted_count} drafts created, {skipped_count} skipped.")
        
        st.session_state.process_clicked = False
        
    except Exception as e:
        st.error(f"❌ Error processing emails: {str(e)}")
        st.exception(e)
        st.session_state.process_clicked = False

st.markdown("---")

# Quick links
st.subheader("📝 Gmail Drafts")
st.info("Check your Gmail drafts folder to review and send the generated responses")

st.link_button(
    "🔗 Open Gmail Drafts",
    "https://mail.google.com/mail/#drafts",
    help="Opens Gmail drafts in a new tab"
)