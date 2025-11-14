# 📧 Email Automation Bot

An intelligent email automation system that uses AI to analyze unread emails, determine if they need responses, and automatically generate draft replies using LLM-powered decision-making.

## 🎯 Features

- **Smart Email Analysis**: Uses Groq's LLaMA 3.3 70B model to analyze email content, intent, and urgency
- **Automated Draft Generation**: Creates contextually appropriate email responses based on analysis
- **Multi-Email Processing**: Processes multiple unread emails in a single run with loop-back workflow
- **Safe Operation**: Creates drafts instead of auto-sending for human review
- **Gmail Integration**: Full OAuth2 authentication and Gmail API integration
- **Intelligent Routing**: LangGraph-based agent with conditional decision-making
- **Category Filtering**: Focus on primary inbox emails, skip promotions and spam
- **Error Handling**: Graceful failure handling with fallback mechanisms

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
│   └── email_agent.py           # LangGraph orchestration
├── utils/
│   └── gmail_auth.py            # OAuth2 authentication
├── main.py                      # Entry point
├── .env                         # API keys (not in repo)
└── requirements.txt             # Dependencies
```

### Workflow Diagram

```
START → Fetch Emails → Select Email → Has Email?
                           ↓              ↓
                      Analyze Email      END
                           ↓
                    Should Respond?
                    ↓           ↓
                Generate    Skip Email
                    ↓           ↓
              Create Draft      ↓
                    ↓___________↓
                    Select Next (loop back)
```

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Gmail account
- Google Cloud Project with Gmail API enabled
- Groq API key

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

5. **First run authentication**
   ```bash
   python main.py
   ```
   - Browser will open for Gmail authorization
   - Grant permissions
   - `token.json` will be created automatically

## 📖 Usage

### Basic Usage

```bash
python main.py
```

The bot will:

1. Fetch unread emails from your primary inbox
2. Analyze each email for intent and urgency
3. Generate draft responses for emails that need replies
4. Save drafts in your Gmail drafts folder
5. Mark processed emails as read

### Example Output

```
🤖 Starting Email Automation Bot...

==================================================
📊 EXECUTION SUMMARY
==================================================
  ✓ Fetched 5 emails
  ✓ Processing email 1/5
  ✓ Analyzed: question
  ✓ generated draft for Project Meeting Request
  ✓ Draft created for: Project Meeting Request
  ✓ Processing email 2/5
  ✓ Analyzed: information
  ✓ Skipped: Newsletter Subscription Confirmation
  ...

📧 Processed 5 emails
✅ Check your Gmail drafts folder!
```

### Customization

**Change number of emails to process:**

Edit `agents/email_agent.py`:

```python
def fetch_email_node(state: EmailAgentState) -> dict:
    result = fetch_unread_emails(service, max_results=10)  # Change from 5 to 10
```

**Change email category filter:**

Edit `agents/email_agent.py`:

```python
result = fetch_unread_emails(
    service,
    max_results=5,
    query='is:unread category:promotions'  # Change to promotions
)
```

**Switch to OpenAI instead of Groq:**

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

## 🧪 Testing

### Test Authentication

```bash
python -c "from utils.gmail_auth import get_gmail_service; service = get_gmail_service(); print('✅ Auth successful')"
```

### Test Gmail Tools

```python
from utils.gmail_auth import get_gmail_service
from tools.gmail_tools import fetch_unread_emails

service = get_gmail_service()
emails = fetch_unread_emails(service, max_results=1)
print(f"Found {len(emails)} unread emails")
```

### Test LLM Analysis

```python
from tools.llm_tools import analyze_email

email_data = {
    'sender': 'test@example.com',
    'subject': 'Meeting Request',
    'body': 'Can we schedule a meeting for tomorrow?'
}

analysis = analyze_email(email_data)
print(analysis)
```

## 🔧 Configuration

### Gmail API Scopes

The bot requires full Gmail access:

```python
SCOPES = ["https://mail.google.com/"]
```

This allows:

- Reading emails
- Creating drafts
- Sending emails (if enabled)
- Modifying labels (marking as read)

### LLM Settings

Adjust in `tools/llm_tools.py`:

```python
llm = ChatGroq(
    api_key=GROQ_API_KEY,
    model=MODEL_NAME,
    temperature=0.3  # Lower = more consistent, Higher = more creative
)
```

### Email Body Truncation

To prevent token limits, emails are truncated:

```python
# In llm_tools.py
body_preview = email_data['body'][:2000]  # Adjust character limit
```

## 🛡️ Security Notes

**Important:**

- Never commit `credentials.json` or `token.json` to version control
- Never commit `.env` file with API keys
- Add to `.gitignore`:
  ```
  .env
  config/credentials.json
  config/token.json
  __pycache__/
  ```

**OAuth Token Management:**

- Tokens are stored locally in `config/token.json`
- Tokens auto-refresh when expired
- Delete `token.json` to re-authenticate

## 🐛 Troubleshooting

### "Error 403: access_denied"

- Add yourself as a test user in Google Cloud Console OAuth consent screen
- Or publish the app (will show warning but works for personal use)

### "Error 413: Request too large"

- Email body is too long for LLM token limit
- Already handled with truncation in `llm_tools.py`
- Adjust truncation limit if needed

### "No module named 'google'"

```bash
pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

### Token expired errors

- Delete `config/token.json`
- Run the bot again to re-authenticate

## 📊 Technology Stack

- **LangGraph**: Agent orchestration and workflow management
- **LangChain**: LLM integration framework
- **Groq API**: Fast LLM inference (LLaMA 3.3 70B)
- **Gmail API**: Email operations
- **OAuth2**: Secure authentication
- **Python 3.8+**: Core language

## 🚧 Future Enhancements

- [ ] Human-in-the-loop approval before creating drafts
- [ ] Multiple email account support
- [ ] Scheduled execution (cron job)
- [ ] Email templates for common responses
- [ ] Analytics dashboard (emails processed, response rate)
- [ ] Custom rules engine (skip certain senders, prioritize domains)
- [ ] Slack/Discord notifications
- [ ] Web UI for configuration

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 👨‍💻 Author

Your Name - [@yourhandle](https://twitter.com/yourhandle)

Project Link: [https://github.com/yourusername/email-automation-bot](https://github.com/yourusername/email-automation-bot)

## 🙏 Acknowledgments

- Built as part of AI Engineer Learning Path - Phase 3 (Agents, Tools, and Automation)
- Inspired by the need to manage inbox overload efficiently
- Thanks to Anthropic, OpenAI, and Groq for providing powerful AI models

## 📚 Related Projects

- [AI Research Assistant](https://github.com/yourusername/ai-research-assistant) - Multi-agent research system
- [Business Report Generator](https://github.com/yourusername/business-report-generator) - Automated report creation

---

⭐ **If you found this project helpful, please consider giving it a star!** ⭐
