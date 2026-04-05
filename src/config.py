import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# LLM
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "http://127.0.0.1:8000/v1/")
LLM_MODEL = os.getenv("LLM_MODEL", "cognitivecomputations/Qwen3-30B-A3B-AWQ")
LLM_API_KEY = os.getenv("LLM_API_KEY", "EMPTY")

# База данных
DATABASE_PATH = BASE_DIR / os.getenv("DATABASE_PATH", "data/emira.db")

# Сервер
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8080"))
