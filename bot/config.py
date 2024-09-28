import os

import openai
from dotenv import load_dotenv

load_dotenv()

# Load environment variables
TOKEN_TELEGRAM = os.getenv("TOKEN_TELEGRAM")
OPENAI_API = os.getenv("OPENAI_API")
MONGO_URL = os.getenv("MONGO_URL")

client = openai.OpenAI(api_key=OPENAI_API)
