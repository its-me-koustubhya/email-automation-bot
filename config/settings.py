import os
from dotenv import load_dotenv

load_dotenv()

# API Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME")

# File paths
CREDENTIALS_FILE = "config/credentials.json"
TOKEN_FILE = "config/token.json"

# Gmail scope
GMAIL_SCOPES = ["https://mail.google.com/"]