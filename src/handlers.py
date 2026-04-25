"""
Bot handlers for processing user messages and commands
"""
from datetime import date, datetime
from aiogram import Bot, F, Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart

from states import AuthForm, InternForm, WorkSession
from parser import ReportParser, TemplateGenerator
from database import db
from keyboards import (
    get_main_keyboard,
    get_login_keyboard,
    get_cancel_keyboard,
    get_yes_no_keyboard
)
from config import (
    BTN_DARS_KIRITISH,
    BTN_ISH_TUGATDIM,
    BTN_CANCEL,
    MSG_WELCOME,
    MSG_TEMPLATE_REQUEST,
    MSG_SUCCESS,
    MSG_ATTENDANCE_CHECK
)
from interns import INTERNS

router = Router()


async def notify_admins(bot: Bot, text: str, sender_id: int = None):
    """Send notification text to all admins"""
    for admin in db.get_admins():
        admin_id = admin['user_id']
        if sender_id and admin_id == sender_id:
            continue

        try:
            await bot.send_message(admin_id, text)
        except Exception as e:
            print(f"❌ Admin notification error ({admin_id}): {e}")


# ===================== AUTHENTICATION =====================

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    """Handle /start command - restore daily session or ask for login"""
    await state.clear()

    daily_session = db.get_daily_user_session(message.from_user.id)
    if daily_session and daily_session.get('attendance_confirmed'):
        intern_name = daily_session['intern_name']
        attendance_status = daily_session.get('attendance_status')

        if attendance_status == 'present':
            await state.update_data(authenticated_intern=intern_name)
            await message.answer(
                f"👋 Xush kelibsiz, {intern_name}!\n\n"
                "Bugungi ro'yxatdan o'tish allaqachon tasdiqlangan.",
                reply_markup=get_main_keyboard()
            )
            return

        await message.answer(
            f"👋 {intern_name}, bugungi holatingiz allaqachon qayd qilingan: kelmayman.",
            reply_markup=get_login_keyboard()
        )
        return

    await message.answer(
        "👤 Ism familyasi (login) yuboring:\n\n"
        "Misol: Ahmadjonov Salohiddin",
        reply_markup=get_login_keyboard()
    )
    await state.set_state(AuthForm.waiting_for_login)


@router.message(AuthForm.waiting_for_login, F.text == BTN_CANCEL)
async def cancel_login(message: Message, state: FSMContext):
    """Cancel login"""
    await message.answer("Bekor qilindi.")
    await state.clear()


@router.message(AuthForm.waiting_for_login, F.text == "🚪 Chiqish")
async def logout_from_waiting_login(message: Message, state: FSMContext):
    """Handle logout while waiting for login"""
    await logout(message, state)


@router.message(AuthForm.waiting_for_login)
async def process_login(message: Message, state: FSMContext):
    """Process login (intern name)"""
    login = message.text.strip()
    
    # Check if it's a valid intern name
    if login not in INTERNS:
        await message.answer(
            "❌ Bu ro'yxatda yo'q.\n\n"
            "Qayta yuboring yoki \"❌ Bekor qilish\" tugmasini bosing.",
            reply_markup=get_login_keyboard()
        )
        return
    
    # Store login and ask for password
    await state.update_data(login=login)
    await state.set_state(AuthForm.waiting_for_password)
    
    await message.answer(
        f"🔐 {login} uchun parolni yuboring:",
        reply_markup=get_login_keyboard()
    )


@router.message(AuthForm.waiting_for_password, F.text == BTN_CANCEL)
async def cancel_password(message: Message, state: FSMContext):
    """Cancel password entry"""
    await message.answer(
        "👤 Qayta ism familyasi (login) yuboring:",
        reply_markup=get_login_keyboard()
    )
    await state.set_state(AuthForm.waiting_for_login)


@router.message(AuthForm.waiting_for_password, F.text == "🚪 Chiqish")
async def logout_from_waiting_password(message: Message, state: FSMContext):
    """Handle logout while waiting for password"""
    await logout(message, state)


@router.message(AuthForm.waiting_for_password)
async def process_password(message: Message, state: FSMContext):
    """Process password"""
    password = message.text.strip()
    data = await state.get_data()
    login = data.get('login')
    
    # Verify credentials
    if not db.verify_login(login, password):
        await message.answer(
            "❌ Parol noto'g'ri.\n\nQayta yuboring.",
            reply_markup=get_login_keyboard()
        )
        return
    
    daily_session = db.get_daily_user_session(message.from_user.id)
    db.upsert_daily_user_session(
        message.from_user.id,
        login,
        username=message.from_user.username or message.from_user.full_name
    )
    await state.update_data(authenticated_intern=login)

    if daily_session and daily_session.get('attendance_confirmed'):
        if daily_session.get('attendance_status') == 'present':
            await message.answer(
                f"👋 Xush kelibsiz, {login}!\n\n"
                "Bugungi ro'yxatdan o'tish allaqachon tasdiqlangan.",
                reply_markup=get_main_keyboard()
            )
        else:
            await message.answer(
                f"👋 {login}, bugungi holatingiz allaqachon qayd qilingan: kelmayman.",
                reply_markup=get_login_keyboard()
            )
        db.add_log(message.from_user.id, "login_successful", f"Intern: {login}")
        return

    # Authentication successful - ask for daily attendance once
    await state.set_state(AuthForm.confirming_attendance)
    
    await message.answer(
        f"👋 Xush kelibsiz, {login}!\n\n{MSG_ATTENDANCE_CHECK}",
        reply_markup=get_yes_no_keyboard()
    )
    db.add_log(message.from_user.id, "login_successful", f"Intern: {login}")


@router.message(AuthForm.confirming_attendance, F.text == "✅ Ha")
async def confirm_attendance_yes(message: Message, state: FSMContext):
    """Intern confirmed they are present - auto-start work session"""
    data = await state.get_data()
    login = data.get('authenticated_intern')
    
    await state.clear()
    await state.update_data(authenticated_intern=login)
    
    await message.answer(
        f"✅ Qayd qilindi!\n\n{MSG_WELCOME}",
        reply_markup=get_main_keyboard()
    )
    db.upsert_daily_user_session(
        message.from_user.id,
        login,
        username=message.from_user.username or message.from_user.full_name,
        attendance_confirmed=True,
        attendance_status='present'
    )
    db.add_log(message.from_user.id, "attendance_confirmed", f"Intern: {login}, Status: Present")
    
    # Auto-start work session
    if db.start_work_session(
        login,
        user_id=message.from_user.id,
        username=message.from_user.username or message.from_user.full_name
    ):
        await message.answer(
            f"🟢 Ish avtomatik boshlandi!\n\n"
            f"👤 {login}\n"
            f"⏰ Vaqt: {datetime.now().strftime('%H:%M:%S')}"
        )
        db.add_log(message.from_user.id, "auto_work_session_started", f"{login}")


@router.message(AuthForm.confirming_attendance, F.text == "❌ Yo'q")
async def confirm_attendance_no(message: Message, state: FSMContext):
    """Intern confirmed they are absent"""
    data = await state.get_data()
    login = data.get('authenticated_intern')
    
    await state.clear()
    await state.update_data(authenticated_intern=login)
    
    await message.answer(
        f"Yaxshi, bugun kelmayotganingiz qayd qilindi.",
        reply_markup=get_login_keyboard()
    )
    db.upsert_daily_user_session(
        message.from_user.id,
        login,
        username=message.from_user.username or message.from_user.full_name,
        attendance_confirmed=True,
        attendance_status='absent'
    )
    db.add_log(message.from_user.id, "attendance_confirmed", f"Intern: {login}, Status: Absent")


@router.message(AuthForm.confirming_attendance, F.text == "🚪 Chiqish")
async def logout_from_confirming_attendance(message: Message, state: FSMContext):
    """Handle logout while confirming attendance"""
    await logout(message, state)


# Helper function to check authentication
async def check_authentication(state: FSMContext, message: Message) -> str:
    """Check if user is authenticated, return intern name or None"""
    data = await state.get_data()
    authenticated_intern = data.get('authenticated_intern')

    if not authenticated_intern:
        daily_session = db.get_daily_user_session(message.from_user.id)
        if daily_session and daily_session.get('attendance_confirmed') and daily_session.get('attendance_status') == 'present':
            authenticated_intern = daily_session.get('intern_name')
            await state.update_data(authenticated_intern=authenticated_intern)

    if not authenticated_intern:
        await message.answer(
            "❌ Avval bazaviy ro'yxatdan o'ting.\n"
            "/start ni bosing.",
            reply_markup=get_login_keyboard()
        )
        return None
    
    return authenticated_intern


# ===================== MAIN MENU =====================

@router.message(F.text == "🚪 Chiqish")
async def logout(message: Message, state: FSMContext):
    """Handle logout"""
    data = await state.get_data()
    intern_name = data.get('authenticated_intern')

    if not intern_name:
        daily_session = db.get_daily_user_session(message.from_user.id)
        if daily_session:
            intern_name = daily_session.get('intern_name')

    await state.clear()
    db.delete_daily_user_session(message.from_user.id)
    await message.answer(
        f"👋 Xayr, {intern_name}!\n\n"
        "Qaytadan kirish uchun /start ni bosing.",
        reply_markup=get_login_keyboard()
    )
    if intern_name:
        db.add_log(message.from_user.id, "logout", f"Intern: {intern_name}")


# ===================== WORK SESSION =====================

@router.message(F.text.in_({BTN_ISH_TUGATDIM, "🔴 Ish tugatim"}))
async def end_work_session(message: Message, state: FSMContext):
    """Handle work session end"""
    intern_name = await check_authentication(state, message)
    if not intern_name:
        return
    
    active_session = db.get_work_session(intern_name)
    
    if active_session:
        # End the session
        if db.end_work_session(
            intern_name,
            ended_by_user_id=message.from_user.id,
            ended_by_username=message.from_user.username or message.from_user.full_name
        ):
            start_time = datetime.fromisoformat(active_session['start_time'])
            end_time = datetime.now()
            duration = int((end_time - start_time).total_seconds() / 60)
            hours = duration // 60
            minutes = duration % 60
            
            await message.answer(
                f"✅ Ish tugatildi!\n\n"
                f"👤 {intern_name}\n"
                f"⏱️ Vaqt: {hours}h {minutes}m\n",
                reply_markup=get_main_keyboard()
            )
            db.add_log(message.from_user.id, "work_session_ended", f"{intern_name}: {duration}min")
        else:
            await message.answer(
                "❌ Xato: Ish tugatilmadi",
                reply_markup=get_main_keyboard()
            )
    else:
        await message.answer(
            f"❌ Faol ish sessiyasi topilmadi",
            reply_markup=get_main_keyboard()
        )


# ===================== LESSON ENTRY =====================

@router.message(F.text == BTN_DARS_KIRITISH)
async def btn_dars_kiritish(message: Message, state: FSMContext):
    """Handle 'Dars kiritish' button"""
    intern_name = await check_authentication(state, message)
    if not intern_name:
        return
    
    await state.update_data(authenticated_intern=intern_name, intern_name=intern_name)
    await state.set_state(InternForm.waiting_for_report)
    
    template = TemplateGenerator.generate_template()
    
    await message.answer(
        f"Tanlandi: {intern_name}\n\n"
        f"Shu shablonni to'ldirib yuboring:\n\n"
        f"<code>{template}</code>\n\n"
        f"{MSG_TEMPLATE_REQUEST}",
        reply_markup=get_cancel_keyboard()
    )


@router.message(InternForm.waiting_for_report, F.text == BTN_CANCEL)
async def cancel_report(message: Message, state: FSMContext):
    """Cancel report submission"""
    await message.answer(
        "Bekor qilindi. Bosh menyudan boshlang.",
        reply_markup=get_main_keyboard()
    )
    await state.set_state(None)


@router.message(InternForm.waiting_for_report, F.text == "🚪 Chiqish")
async def logout_from_waiting_report(message: Message, state: FSMContext):
    """Handle logout while waiting for report"""
    await logout(message, state)


@router.message(InternForm.waiting_for_report)
async def process_report(message: Message, state: FSMContext):
    """Process submitted report"""
    text = message.text
    
    # Check if message starts with #hisobot
    if '#hisobot' not in text.lower():
        await message.answer(
            "❌ Shablonni topilmadi. '#hisobot' bilan boshlang.",
            reply_markup=get_cancel_keyboard()
        )
        return
    
    # Parse report
    parsed_data = ReportParser.parse_report(text)
    
    if not parsed_data:
        error_msg = ReportParser.get_error_message(parsed_data if parsed_data else {})
        await message.answer(
            f"❌ Xato: {error_msg}\n\n{MSG_TEMPLATE_REQUEST}",
            reply_markup=get_cancel_keyboard()
        )
        return
    
    # Get authenticated intern name
    data = await state.get_data()
    authenticated_intern = data.get('authenticated_intern')
    
    # Verify intern name matches
    if parsed_data['intern_name'] != authenticated_intern:
        await message.answer(
            f"❌ Tanlovangiz: {authenticated_intern}\n"
            f"Shaklondagi: {parsed_data['intern_name']}\n\n"
            f"Nomlar mos kelmadi. Qayta urinib ko'ring.",
            reply_markup=get_cancel_keyboard()
        )
        return
    
    # Store parsed data in state
    parsed_data['status'] = 'Keldi'
    parsed_data['user_id'] = message.from_user.id
    parsed_data['username'] = message.from_user.username or message.from_user.full_name
    parsed_data['raw_text'] = text
    await state.update_data(parsed_report=parsed_data)
    await state.set_state(InternForm.confirming_report)
    
    # Show confirmation
    lesson_list = '\n'.join([
        f"  🔹 Dars #{lesson['number']}: {lesson['teacher']} ({lesson['time']})"
        for lesson in parsed_data['lessons']
    ])
    
    confirmation_text = (
        f"✅ Hisobot tahlili qabul qilindi!\n\n"
        f"👤 Intern: {parsed_data['intern_name']}\n"
        f"📅 Sana: {parsed_data['date'].strftime('%d.%m.%Y')}\n"
        f"🕒 Kelgan: {parsed_data['arrival_time']}\n"
        f"🕒 Ketgan: {parsed_data['departure_time']}\n"
        f"📚 Darslar ({len(parsed_data['lessons'])} ta):\n"
        f"{lesson_list}\n\n"
        f"To'g'rimi?"
    )
    
    await message.answer(
        confirmation_text,
        reply_markup=get_yes_no_keyboard()
    )


@router.message(InternForm.confirming_report, F.text == "✅ Ha")
async def confirm_report(message: Message, state: FSMContext):
    """Confirm and save report"""
    data = await state.get_data()
    parsed_report = data.get('parsed_report')
    
    if not parsed_report:
        await message.answer(
            "❌ Hisobot ma'lumotlari yo'q. Qayta boshlang.",
            reply_markup=get_main_keyboard()
        )
        await state.set_state(None)
        return
    
    # Save to database
    success = db.add_report(parsed_report)
    
    if success:
        await message.answer(
            f"{MSG_SUCCESS}\n\n"
            f"Rahmat, {parsed_report['intern_name']}!",
            reply_markup=get_main_keyboard()
        )
    else:
        await message.answer(
            "❌ Database xatosi. Admin bilan bog'laning.",
            reply_markup=get_main_keyboard()
        )
    
    await state.set_state(None)


@router.message(InternForm.confirming_report, F.text == "❌ Yo'q")
async def reject_report(message: Message, state: FSMContext):
    """Reject and re-submit"""
    data = await state.get_data()
    authenticated_intern = data.get('authenticated_intern')
    
    template = TemplateGenerator.generate_template()
    
    await message.answer(
        f"Qaytadan to'ldirib yuboring:\n\n"
        f"<code>{template}</code>\n\n"
        f"{MSG_TEMPLATE_REQUEST}",
        reply_markup=get_cancel_keyboard()
    )
    
    await state.set_state(InternForm.waiting_for_report)


@router.message(InternForm.confirming_report, F.text == "🚪 Chiqish")
async def logout_from_confirming_report(message: Message, state: FSMContext):
    """Handle logout while confirming report"""
    await logout(message, state)


# ===================== FALLBACK =====================

@router.message()
async def echo(message: Message, state: FSMContext):
    """Handle unknown messages"""
    data = await state.get_data()
    authenticated_intern = data.get('authenticated_intern')
    
    if not authenticated_intern:
        await message.answer(
            "❌ Avval bazaviy ro'yxatdan o'ting.\n"
            "/start ni bosing.",
            reply_markup=get_login_keyboard()
        )
    else:
        await message.answer(
            "❌ Noto'g'ri buyruq.\n\n"
            "Bosh menyudan tanlang:",
            reply_markup=get_main_keyboard()
        )
