from dotenv import load_dotenv
import os

from openai import OpenAI

load_dotenv()
 
DATABASE_URL = os.getenv("DATABASE_URL")
SENTRY_DSN = os.getenv("SENTRY_DSN")
SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
MAX_BCRYPT_LEN = 72

# OpenAI Client
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai_client = OpenAI(api_key=OPENAI_API_KEY)