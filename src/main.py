"""
Main bot entry point
"""
import asyncio
import logging
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from aiogram import Dispatcher, Bot, F
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand

from config import BOT_TOKEN, TIMEZONE
from handlers import router
from admin import admin_router
from admin_init import setup_admin  # Initialize admin
from database import db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def set_commands(bot: Bot):
    """Set bot commands"""
    commands = [
        BotCommand(command='start', description='Botni boshlash'),
        BotCommand(command='help', description='Yordam'),
    ]
    await bot.set_my_commands(commands)


async def auto_absence_scheduler(bot: Bot):
    """Mark yesterday's missing interns as absent after midnight"""
    tz = ZoneInfo(TIMEZONE)
    last_processed_report_date = None

    while True:
        try:
            now = datetime.now(tz)
            report_date = now.date() - timedelta(days=1)

            if last_processed_report_date != report_date:
                missing_interns = db.auto_mark_absent_for_date(report_date)

                if missing_interns:
                    notification = (
                        f"⏰ 00:00 dan keyingi avtomatik tekshiruv bajarildi\n"
                        f"📅 Sana: {report_date.strftime('%d.%m.%Y')}\n\n"
                        "Quyidagi internlar avtomatik 'Kelmadi' deb belgilandi:\n"
                        + "\n".join(f"• {intern}" for intern in missing_interns)
                    )
                    for admin in db.get_admins():
                        try:
                            await bot.send_message(admin['user_id'], notification)
                        except Exception as e:
                            logger.warning("Admin notification failed for %s: %s", admin['user_id'], e)

                last_processed_report_date = report_date
        except Exception as e:
            logger.exception("Auto absence scheduler error: %s", e)

        await asyncio.sleep(60)


async def main():
    """Main bot function"""
    
    # Initialize admin
    setup_admin()
    
    # Check if token is set
    if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        logger.error("❌ BOT_TOKEN not set in .env file!")
        print("❌ BOT_TOKEN not set in .env file!")
        print("   Please create .env file with: BOT_TOKEN=your_token_here")
        return
    
    # Initialize bot and dispatcher
    storage = MemoryStorage()
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=storage)
    
    # Include routers
    dp.include_router(admin_router)  # Admin commands first (higher priority)
    dp.include_router(router)         # Regular user commands

    scheduler_task = asyncio.create_task(auto_absence_scheduler(bot))
    
    # Set bot commands
    await set_commands(bot)
    
    logger.info("✅ Bot started successfully")
    print("✅ Bot started successfully!")
    print("   Waiting for messages...")
    
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        scheduler_task.cancel()
        try:
            await scheduler_task
        except asyncio.CancelledError:
            pass
        await bot.session.close()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n❌ Bot stopped")
        logger.info("Bot stopped by user")
