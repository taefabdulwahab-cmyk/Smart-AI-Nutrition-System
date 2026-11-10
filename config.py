import os
from dotenv import load_dotenv
load_dotenv()
MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
CARB_LIMIT_G = 45
SODIUM_LIMIT_MG = 600
