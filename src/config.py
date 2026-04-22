"""
Configuration file for the Telegram Bot
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Bot token
BOT_TOKEN = os.getenv("BOT_TOKEN", "")

# Database file path
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

EXCEL_FILE = DATA_DIR / "interns_reports.xlsx"

# Timezone
TIMEZONE = "Asia/Tashkent"

# Admin settings
ADMIN_ID = 7782143104, 865954550, 1038185913  # Set your admin ID for notifications

# Button labels (in Uzbek)
BTN_DARS_KIRITISH = "📚 Dars kiritish"
BTN_HISOBOT = "📋 Hisobot"
BTN_CANCEL = "❌ Bekor qilish"
BTN_ISSUE_REPORT = "⚠️ Muammoni yozing"
BTN_ABSENCE_REASON = "📝 Sabab kiritish"

# Messages
MSG_WELCOME = "Assalamu alaykum! Keling boshlaylik."
MSG_SELECT_INTERNSHIP = "Kechirasiz, avvalo o'zingizni tanlang:"
MSG_TEMPLATE_REQUEST = "Iltimos, shu shablonni to'ldirib yuboring."
MSG_TEMPLATE_ERROR = "❌ Shablonni noto'g'ri to'ldirdingiz. Iltimos qayta urinib ko'ring."
MSG_SUCCESS = "✅ Hisobot qabul qilindi!"
MSG_ABSENCE = "Nega kelmadingiz?"
