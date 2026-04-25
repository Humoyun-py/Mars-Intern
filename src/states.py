"""
FSM (Finite State Machine) states for the bot
"""
from aiogram.fsm.state import State, StatesGroup


class AuthForm(StatesGroup):
    """States for intern authentication"""
    waiting_for_login = State()
    waiting_for_password = State()
    confirming_attendance = State()


class InternForm(StatesGroup):
    """States for intern report form"""
    waiting_for_report = State()
    confirming_report = State()


class WorkSession(StatesGroup):
    """States for work session management"""
    selecting_intern_start = State()
    selecting_intern_end = State()
