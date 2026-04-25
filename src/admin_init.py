"""
Admin setup and initialization
"""
from database import db
from interns import INTERNS

# Default admin user ID - change this to your Telegram ID
DEFAULT_ADMIN_ID = 7782143104  # Set your admin user ID here


def setup_admin():
    """Initialize admin users and intern credentials"""
    if DEFAULT_ADMIN_ID:
        if not db.is_admin(DEFAULT_ADMIN_ID):
            db.add_admin(DEFAULT_ADMIN_ID, "Admin")
            print(f"✅ Admin qo'shildi: {DEFAULT_ADMIN_ID}")
    
    # Initialize intern credentials with default password
    print("🔐 Internlar uchun parollar tekshirilmoqda...")
    for intern_name in INTERNS:
        cred = db.get_intern_credentials(intern_name)
        if not cred:
            db.set_password(intern_name, "12345678")
            print(f"   ✅ {intern_name}: parol o'rnatildi")
    
    return True

