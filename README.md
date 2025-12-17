# 📧 Email Automation Bot

An intelligent email automation system with both CLI and web interface that uses AI to analyze unread emails, determine if they need responses, and automatically generate draft replies using LLM-powered decision-making.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)

## 🎯 Features

### Core Functionality

- **Smart Email Analysis**: Uses Groq's LLaMA 3.3 70B model to analyze email content, intent, and urgency
- **Automated Draft Generation**: Creates contextually appropriate email responses based on analysis
- **Multi-Email Processing**: Processes multiple unread emails in a single run with intelligent routing
- **Safe Operation**: Creates drafts instead of auto-sending for human review
- **Gmail Integration**: Full OAuth2 authentication and Gmail API integration

### Web Interface (Streamlit)

- **User Authentication**: Secure multi-user support with bcrypt password hashing
- **Visual Dashboard**: Clean, intuitive interface for email review and processing
- **Real-time Metrics**: Track processed emails, drafts created, and skipped emails
- **Activity History**: View all past actions and decisions
- **Configurable Settings**: Customize email processing preferences per user
- **Responsive Design**: Works seamlessly across different screen sizes

### Intelligence Features

- **Category Detection**: Automatically categorizes emails (question, request, information, spam)
- **Urgency Analysis**: Determines priority levels (high, medium, low)
- **Smart Filtering**: Focus on primary inbox emails, skip promotions
- **Auto-Skip Logic**: Automatically marks emails that don't need responses as read
- **Error Handling**: Graceful failure handling with detailed error messages

## 🏗️ Architecture

```
email_automation_bot/
├── config/
│   ├── settings.py              # Configuration management
│   └── credentials.json         # Gmail OAuth credentials (not in repo)
├── tools/
│   ├── gmail_tools.py           # Gmail API operations (fetch, send, draft)
│   └── llm_tools.py             # LLM analysis and generation
├── agents/
│   └── email_agent.py           # LangGraph orchestration (CLI)
├── utils/
│   └── gmail_auth.py            # OAuth2 authentication
├── streamlit_app/
│   ├── app.py                   # Web app entry point
│   ├── components/
│   │   ├── auth.py              # User authentication
│   │   ├── user_config.py       # User configuration management
│   │   └── gmail_setup.py       # Gmail OAuth per user
│   ├── pages/
│   │   ├── 1_🏠_Dashboard.py    # Email processing interface
│   │   ├── 2_⚙️_Settings.py     # User settings
│   │   └── 3_📊_History.py      # Activity logs
│   └── data/                    # User data (not in repo)
├── main.py                      # CLI entry point
└── requirements.txt             # Dependencies
```

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Gmail account
- Google Cloud Project with Gmail API enabled
- Groq API key (free at [console.groq.com](https://console.groq.com))

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/yourusername/email-automation-bot.git
   cd email-automation-bot
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Set up Google Cloud & Gmail API**

   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project
   - Enable Gmail API
   - Create OAuth 2.0 credentials (Desktop App)
   - Download `credentials.json` and place in `config/` folder
   - Add yourself as a test user in OAuth consent screen

4. **Configure environment variables**

   Create a `.env` file in the root directory:

   ```env
   GROQ_API_KEY=your_groq_api_key_here
   MODEL_NAME=llama-3.3-70b-versatile
   ```

## 📖 Usage

### Option 1: Web Interface (Recommended)

**Start the Streamlit app:**

```bash
streamlit run streamlit_app/app.py
```

**First-time setup:**

1. **Sign Up**: Create an account with username, email, and password
2. **Login**: Access your personal dashboard
3. **Connect Gmail**:
   - Click "Connect Gmail" link
   - Authorize with your Google account
   - Copy the authorization code
   - Paste it in the app
4. **Add API Key**: Enter your Groq API key in the setup wizard
5. **Start Processing**: Navigate to Dashboard and click "Process Emails"

**Features:**

- 🏠 **Dashboard**: Process emails, review drafts, create Gmail drafts
- ⚙️ **Settings**: Configure API keys, set max emails per run, choose categories
- 📊 **History**: View all past actions and processing history

### Option 2: Command Line Interface

**First run (authentication):**

```bash
python main.py
```

Browser will open for Gmail authorization. Grant permissions and `token.json` will be created automatically.

**Subsequent runs:**

```bash
python main.py
```

The CLI bot will:

1. Fetch unread emails from your primary inbox
2. Analyze each email for intent and urgency
3. Generate draft responses for emails that need replies
4. Save drafts in your Gmail drafts folder
5. Mark processed emails as read

## 🎨 Web Interface Screenshots

### Dashboard

- Clean interface showing email metrics
- Visual highlighting for emails needing review
- Inline draft preview and approval
- Real-time status updates

### Settings

- API key management
- Gmail connection status
- Processing preferences (max emails, categories, auto-mark read)
- Account information

### History

- Complete activity log
- Filter by action type
- Detailed view of each action
- Statistics summary

## ⚙️ Configuration

### Email Processing Settings

Customize in **Settings** page or edit user config:

```json
{
  "groq_api_key": "your_key_here",
  "settings": {
    "max_emails": 10,
    "categories": ["primary"],
    "auto_mark_read": true
  }
}
```

**Available Options:**

- `max_emails`: Number of emails to process per run (1-50)
- `categories`: Which Gmail categories to process (`primary`, `social`, `promotions`, `updates`)
- `auto_mark_read`: Automatically mark processed emails as read

### LLM Settings

Adjust in `tools/llm_tools.py`:

```python
llm = ChatGroq(
    api_key=GROQ_API_KEY,
    model=MODEL_NAME,
    temperature=0.3  # Lower = more consistent, Higher = more creative
)
```

## 🔧 Advanced Usage

### Custom Email Queries

Modify the Gmail query in Dashboard or `main.py`:

```python
fetch_unread_emails(
    service,
    max_results=10,
    query='is:unread category:primary'  # Customize this
)
```

**Query Examples:**

- `is:unread category:social` - Social emails only
- `is:unread from:example.com` - Specific sender
- `is:unread newer_than:1d` - Last 24 hours only

### Switching LLM Providers

**To use OpenAI instead of Groq:**

Update `.env`:

```env
OPENAI_API_KEY=your_openai_key
MODEL_NAME=gpt-4o-mini
```

Update `tools/llm_tools.py`:

```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    api_key=OPENAI_API_KEY,
    model=MODEL_NAME,
    temperature=0.3
)
```

Add to `requirements.txt`:

```
langchain-openai==0.3.15
```

## 🛡️ Security & Privacy

### Data Storage

- **User credentials**: Encrypted with bcrypt, stored locally in `streamlit_app/data/users.yaml`
- **Gmail tokens**: Stored per-user in `streamlit_app/data/users/{username}/token.json`
- **API keys**: Stored locally, never transmitted except to respective API services
- **History logs**: Stored locally per user

### Gmail API Permissions

- **Scope**: `https://mail.google.com/` (full Gmail access)
- **What we access**: Read emails, create drafts, modify labels (mark as read)
- **What we DON'T do**: Delete emails, access contacts, send emails without drafts

### Best Practices

- ✅ Never commit `credentials.json` or `token.json`
- ✅ Never commit `.env` file with API keys
- ✅ Add sensitive files to `.gitignore`
- ✅ Use test users in Google OAuth consent screen for development
- ✅ Regularly rotate API keys

**Important files in `.gitignore`:**

```
.env
config/credentials.json
config/token.json
streamlit_app/data/
```

## 🐛 Troubleshooting

### "Error 403: access_denied"

**Solution:** Add yourself as a test user in Google Cloud Console OAuth consent screen

- Go to APIs & Services → OAuth consent screen
- Add your email under "Test users"

### "Error 413: Request too large"

**Solution:** Email body exceeds LLM token limit

- Already handled with truncation in `llm_tools.py`
- Bodies are limited to 2000 characters for analysis
- Adjust `body_preview = email_data['body'][:2000]` if needed

### "Module not found"

**Solution:** Install dependencies

```bash
pip install -r requirements.txt
```

### Gmail authorization fails

**Solution:** Delete expired tokens and re-authenticate

```bash
rm config/token.json  # For CLI
rm streamlit_app/data/users/{username}/token.json  # For web app
```

### Token expired errors

**Solution:** Tokens auto-refresh, but if issues persist:

- Delete token file
- Re-authenticate through the app

### Streamlit app not loading

**Solution:** Check port availability

```bash
streamlit run streamlit_app/app.py --server.port 8502  # Use different port
```

## 📊 Technology Stack

- **LangGraph**: Agent orchestration and workflow management
- **LangChain**: LLM integration framework
- **Groq API**: Fast LLM inference (LLaMA 3.3 70B)
- **Streamlit**: Web application framework
- **Gmail API**: Email operations via Google APIs
- **OAuth2**: Secure authentication
- **BCrypt**: Password hashing and security
- **Python 3.8+**: Core language

## 🎓 How It Works

### Email Processing Flow

```
1. Fetch Unread Emails
   ↓
2. For each email:
   ├─ Analyze with LLM (category, urgency, intent)
   ├─ Should respond?
   │  ├─ Yes → Generate draft response
   │  └─ No → Auto-skip and mark as read
   ↓
3. Present drafts for review (Web UI)
   ├─ User approves → Create draft in Gmail
   └─ User skips → Mark as read
   ↓
4. Log action to history
```

### LangGraph Agent (CLI Version)

```
START → Fetch Emails → Select Email → Has Email?
                           ↓              ↓
                      Analyze Email     END
                           ↓
                    Should Respond?
                    ↓           ↓
              Generate      Skip Email
                    ↓           ↓
              Create Draft    ↓
                    ↓_________↓
                    Select Next (loop back)
```

## 🚧 Future Enhancements

### Planned Features

- [ ] Email templates for common response types
- [ ] Scheduled processing (cron jobs)
- [ ] Email threading and conversation context
- [ ] Multiple Gmail account support per user
- [ ] Slack/Discord notifications for new drafts
- [ ] Analytics dashboard (response rate, processing time)
- [ ] Custom rules engine (skip certain senders, prioritize domains)
- [ ] Mobile-responsive improvements
- [ ] Export history as CSV/PDF
- [ ] Bulk actions (approve all, skip all)

### Advanced Features

- [ ] RAG integration for knowledge-based responses
- [ ] Fine-tuned models for specific use cases
- [ ] Integration with calendar for meeting scheduling
- [ ] Sentiment analysis for priority routing
- [ ] Multi-language support

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

**Guidelines:**

- Follow PEP 8 style guide
- Add tests for new features
- Update documentation
- Keep commits atomic and well-described

## 👨‍💻 Author

Project Link: [https://github.com/its-me-koustubhya/email-automation-bot](https://github.com/its-me-koustubhya/email-automation-bot)

## 🙏 Acknowledgments

- Built as part of AI Engineer Learning Path - Phase 3 (Agents, Tools, and Automation)
- Inspired by the need to manage inbox overload efficiently
- Thanks to Anthropic, Groq, and Google for providing powerful AI and API services
- Special thanks to the LangChain and Streamlit communities

## 📚 Related Learning Resources

- [LangChain Documentation](https://docs.langchain.com)
- [LangGraph Documentation](https://docs.langchain.com/oss/python/langgraph/overview)
- [Groq API Documentation](https://console.groq.com/docs)
- [Gmail API Documentation](https://developers.google.com/gmail/api)
- [Streamlit Documentation](https://docs.streamlit.io)

---

⭐ **If you found this project helpful, please consider giving it a star!** ⭐

**Questions or issues?** Feel free to open an issue or reach out!
