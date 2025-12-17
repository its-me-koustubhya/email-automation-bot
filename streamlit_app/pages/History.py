import streamlit as st
import sys
from pathlib import Path
from datetime import datetime
import pandas as pd

sys.path.append(str(Path(__file__).parent.parent.parent))

from streamlit_app.components.auth import AuthManager
from streamlit_app.components.user_config import UserConfig

st.set_page_config(page_title="History", page_icon="📊", layout="wide")

# Check authentication
auth = AuthManager()
if not auth.is_authenticated():
    st.warning("⚠️ Please login first")
    st.stop()

st.title("📊 Activity History")

username = auth.get_current_user()
config = UserConfig(username)

# Load history
history = config.load_history()

if not history:
    st.info("📭 No activity yet. Start processing emails to see your history!")
    st.stop()

# Display stats
st.subheader("📈 Summary Statistics")

total_actions = len(history)
drafted = sum(1 for h in history if h['action'] == 'draft_created')
skipped = sum(1 for h in history if h['action'] in ['skipped', 'auto_skipped'])

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Actions", total_actions)
with col2:
    st.metric("Drafts Created", drafted)
with col3:
    st.metric("Emails Skipped", skipped)

st.markdown("---")

# Filter options
st.subheader("🔍 Filter History")

col1, col2 = st.columns(2)

with col1:
    action_filter = st.selectbox(
        "Action Type:",
        options=["All", "draft_created", "skipped", "auto_skipped"],
        index=0
    )

with col2:
    limit = st.slider("Number of entries to show:", 10, 100, 50)

# Filter history
filtered_history = history
if action_filter != "All":
    filtered_history = [h for h in history if h['action'] == action_filter]

# Show recent entries (reverse chronological order)
filtered_history = filtered_history[-limit:]
filtered_history.reverse()

st.markdown("---")

# Display as table
st.subheader("📋 Recent Activity")

if filtered_history:
    # Convert to DataFrame for better display
    df_data = []
    for entry in filtered_history:
        df_data.append({
            'Time': entry['timestamp'].split('T')[1][:8],
            'Date': entry['timestamp'].split('T')[0],
            'Action': entry['action'].replace('_', ' ').title(),
            'Email Subject': entry.get('email', 'N/A')[:50] + '...' if len(entry.get('email', '')) > 50 else entry.get('email', 'N/A'),
            'Sender': entry.get('sender', 'N/A')
        })
    
    df = pd.DataFrame(df_data)
    st.dataframe(df, width='stretch', hide_index=True)
    
    st.markdown("---")
    
    # Detailed view
    st.subheader("🔍 Detailed View")
    
    for i, entry in enumerate(filtered_history[:20]):  # Show top 20 in detail
        with st.expander(f"{entry['timestamp'][:19]} - {entry['action'].replace('_', ' ').title()}"):
            st.json(entry)
else:
    st.info("No entries match your filter criteria")

st.markdown("---")

# Clear history option
st.subheader("⚠️ Danger Zone")

with st.expander("🗑️ Clear All History"):
    st.warning("⚠️ This will permanently delete all your activity history. This action cannot be undone!")
    
    confirm = st.text_input("Type 'DELETE' to confirm:", key="confirm_delete")
    
    if st.button("🗑️ Confirm Clear History", type="primary", disabled=(confirm != "DELETE")):
        import json
        history_file = Path(f"streamlit_app/data/users/{username}/history.json")
        
        try:
            with open(history_file, 'w') as f:
                json.dump([], f)
            st.success("✅ History cleared successfully!")
            st.rerun()
        except Exception as e:
            st.error(f"Error clearing history: {e}")