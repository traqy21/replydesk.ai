"""Application configuration and environment setup."""

import os
from dotenv import load_dotenv
from openai import OpenAI

dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path)

# App metadata
APP_NAME = "Replydesk AI"
APP_CAPTION = "Generate emails, replies, and reports instantly"
MODEL = "gpt-4o-mini"

# OpenAI setup
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise RuntimeError(
        "OPENAI_API_KEY not found. Set it in your environment or in a .env file next to the app."
    )

client = OpenAI(api_key=api_key)
