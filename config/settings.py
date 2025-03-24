import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
SEOUL_API_KEY = os.getenv("SEOUL_API_KEY")
KAKAO_REST_API_KEY = os.getenv("KAKAO_REST_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Default settings
DEFAULT_EVENT_LIMIT = 3
BASE_SEOUL_API_URL = "http://openapi.seoul.go.kr:8088"
KAKAO_API_BASE_URL = "https://dapi.kakao.com/v2/local/search"
