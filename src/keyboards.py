"""
Keyboards and UI components for the bot
"""
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from interns import INTERNS
from config import BTN_DARS_KIRITISH, BTN_CANCEL, BTN_ISSUE_REPORT, BTN_ABSENCE_REASON


def get_main_keyboard() -> ReplyKeyboardMarkup:
    """Get main menu keyboard"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🟢 Ish boshladim"), KeyboardButton(text="🔴 Ish tugatim")],
            [KeyboardButton(text=BTN_DARS_KIRITISH)],
            [KeyboardButton(text=BTN_ABSENCE_REASON)],
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )
    return keyboard


def get_intern_selection_keyboard() -> ReplyKeyboardMarkup:
    """Get keyboard for selecting intern name"""
    buttons = []
    
    # Add intern buttons in rows of 2
    for i in range(0, len(INTERNS), 2):
        row = []
        if i < len(INTERNS):
            row.append(KeyboardButton(text=INTERNS[i]))
        if i + 1 < len(INTERNS):
            row.append(KeyboardButton(text=INTERNS[i + 1]))
        buttons.append(row)
    
    # Add cancel button
    buttons.append([KeyboardButton(text=BTN_CANCEL)])
    
    keyboard = ReplyKeyboardMarkup(
        keyboard=buttons,
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
