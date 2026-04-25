"""
Keyboards and UI components for the bot
"""
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from config import BTN_DARS_KIRITISH, BTN_CANCEL, BTN_ISH_TUGATDIM


def get_main_keyboard() -> ReplyKeyboardMarkup:
    """Get main menu keyboard"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=BTN_ISH_TUGATDIM)],
            [KeyboardButton(text=BTN_DARS_KIRITISH)],
            [KeyboardButton(text="🚪 Chiqish")],
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )
    return keyboard


def get_login_keyboard() -> ReplyKeyboardMarkup:
    """Get keyboard for login (only cancel button)"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=BTN_CANCEL)],
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return keyboard


def get_cancel_keyboard() -> ReplyKeyboardMarkup:
    """Get keyboard with cancel button"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=BTN_CANCEL)],
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return keyboard


def get_yes_no_keyboard() -> ReplyKeyboardMarkup:
    """Get yes/no keyboard"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="✅ Ha"), KeyboardButton(text="❌ Yo'q")],
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return keyboard
