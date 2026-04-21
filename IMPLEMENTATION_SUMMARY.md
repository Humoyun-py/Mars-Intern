# Mars Intern Bot - Yangi Xususiyatlar Qo'shish

## Xulosa
Ushbu implementatsion 3 ta yangi xususiyatni qo'shadi:

### 1. ✅ Admin Excel Export - Fayl Yuklab Olish
**Maqsad:** Admin paneldan Excel faylini to'g'ridan-to'g'ri yuklab olish

**O'zgarishlar:**
- `src/admin.py`:
  - `from aiogram.types` ga `FSInputFile` qo'shildi
  - `from aiogram` ga `Bot` qo'shildi
  - `admin_excel_callback` yangilandi: Endi `bot: Bot` parametrni qabul qiladi
  - Excel fayli yaratilganidan so'ng, `bot.send_document()` orqali faylni admin tomonidan yuklab olinadi
  - Fayl nomida sana bo'ladi: `lessons_export_DD_MM_YYYY.xlsx`

**Ishlash:**
1. Admin `/admin` buyruqni yoki Admin Panel tugmasini bosadi
2. `📥 Excel export` tugmasini bosganda, darslar 90 kun ichida Excel-ga eksport bo'ladi
3. Admin to'g'ridan-to'g'ri Telegram-dan fayl yuklab oladi

---

### 2. ✅ Saot 12:00 Tekshirish - Hisobot Topshirish Muddati
**Maqsad:** Admin bo'lim internlarning hisobotini topshirgani-topshirgani yo'qligini tekshirishi

**O'zgarishlar:**
- `src/admin.py`:
  - Admin Menu-ga `⏰ Saot 12 teksh` tugmasi qo'shildi
  - `admin_check_deadline_callback` funksiyasi qo'shildi
  - Bu funksiya buguning hamma hisobotlarini tekshiradi va topshirmagan internlarni ko'rsatadi

**Ishlash:**
1. Admin `/admin` panelini bosadi
2. `⏰ Saot 12 teksh` tugmasini bosadi
3. Oyna quyidagi ma'lumotlarni ko'rsatadi:
   - Bugun uchun hozirgi vaqt
   - **Hisobot tashamagan internlar ro'yxati** (agar bor bo'lsa)
   - Jami tashamagan internlar soni
4. Admin bu internlar uchun sabab kiritsa bo'ladi

**Eslatma:** Sistema bugun topshirmagan internlarni avtomatik ravishda "Kelmadi" holati bilan qayd qilmaydi, faqat admin tekshirish imkoniyatini beradi.

---

### 3. ✅ Muammo Yozish Tugmasi - User Panel-da
**Maqsad:** Internlar ish jarayonida ishga kemagani sababini yozishlari

**O'zgarishlar:**
- `src/config.py`:
  - Yangi tugma konstantasi qo'shildi: `BTN_ISSUE_REPORT = "⚠️ Muammo yozing"`

- `src/keyboards.py`:
  - `BTN_ISSUE_REPORT` import qo'shildi
  - `get_main_keyboard()` funksiyasida yangi tugma qo'shildi
  - Main keyboard endi 3 qatordan iborat:
    - Qator 1: "🟢 Ish boshladim" | "🔴 Ish tugatim"
    - Qator 2: "📚 Dars kiritish"
    - Qator 3: "⚠️ Muammo yozing" (YANGI)

- `src/states.py`:
  - Yangi FSM State Group qo'shildi: `IssueReport` 
  - State: `writing_issue` - muammo yozish uchun

- `src/handlers.py`:
  - `IssueReport` state import qo'shildi
  - `BTN_ISSUE_REPORT` import qo'shildi
  - `echo` handler yangilandi - "⚠️ Muammo yozing" tugmasini tekshiradi
  - Quyidagi yangi handlers qo'shildi:
    - `process_issue_report()` - muammoni qabul qiladi va bazaga saqlaydi
    - `cancel_issue_report()` - muammo yozishni bekor qilish

**Ishlash:**
1. Intern main keyboard-dan "⚠️ Muammo yozing" tugmasini bosadi
2. Bot tomonidan "Muammo yoki ishga kemagani sababini yozing:" so'rovi
3. Intern rasmiy matnni yozadi (misol: "Kompyuter viruslandi", "Internet yo'q", "Shaxsiy sabab")
4. Muammo `database.logs` jadvaliga saqlanadi
5. Admin logs-dan ko'rishi mumkin

---

## Fayllar O'zgartirildi

### 1. `src/admin.py`
- **Imports:** `datetime`, `Bot`, `FSInputFile` qo'shildi
- **AdminStates:** `writing_issue_reason` state qo'shildi
- **get_back_keyboard():** O'zgarmadi
- **admin_menu():** Admin Menu-ga `⏰ Saot 12 teksh` tugmasi qo'shildi
- **admin_excel_callback():** Bot parametri qo'shildi va Excel fayli yuklab olinadi
- **admin_check_deadline_callback():** YANGI - Topshirmagan internlarni tekshiradi

### 2. `src/handlers.py`
- **Imports:** `IssueReport` state, `BTN_ISSUE_REPORT` button import qo'shildi
- **echo():** Handler yangilandi - "⚠️ Muammo yozing" tugmasini tekshiradi
- **process_issue_report():** YANGI - Muammoni saqlaydi
- **cancel_issue_report():** YANGI - Muammo yozishni bekor qiladi

### 3. `src/keyboards.py`
- **Imports:** `BTN_ISSUE_REPORT` import qo'shildi
- **get_main_keyboard():** Yangi tugma qo'shildi

### 4. `src/states.py`
- **IssueReport:** YANGI FSM State Group qo'shildi

### 5. `src/config.py`
- **BTN_ISSUE_REPORT:** YANGI tugma konstantasi qo'shildi

---

## Testing Checklist

- [x] Syntax barcha fayllar xato yo'q
- [x] Excel export file yuklab olinadi
- [x] Admin saot 12 tekshishi aniq ishlaydi
- [x] Muammo yozish tugmasi ishlaydi
- [x] Muammolar bazaga saqlanadi

---

## Ishlat Bo'lim

### Admin Panel:
1. `/admin` - Admin panelni ochish
2. `📥 Excel export` - Dars ro'yxatini Excel-ga chiqarish
3. `⏰ Saot 12 teksh` - Topshirmagan internlarni tekshirish

### User Panel:
1. `⚠️ Muammo yozing` - Muammo yoki sabab yozish

---

## Database O'zgarishlari
- Hech qanday jadval qo'shilmadi (logs jadvalidan foydalaniladi)
- Muammolar `logs` jadvalidagi `action: "issue_reported"` bilan saqlanadi

---

## Eslatma
- Saot 12:00 tekshirish vaqti 00:00 (yarim tun) asosida solishtirilyapti
- Admin mo'jroida Excel faylni o'zi yuklab olib, keyin tarqatishi mumkin
- Muammolar admin logsda "issue_reported" action bilan ko'rinadi
