from dotenv import load_dotenv
import os

load_dotenv()
 
DATABASE_URL = os.getenv("DATABASE_URL")
SENTRY_DSN = os.getenv("SENTRY_DSN")
SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30