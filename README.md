# Mars Intern - Telegram Bot

## Overview
A Telegram bot for tracking intern attendance and daily lesson reports at Mars Internship. The bot uses FSM (Finite State Machine) to manage user interactions and stores data in Excel.

## Features
- ✅ Intern name selection with reply keyboard
- ✅ Report template generation and submission
- ✅ Automatic parsing of lesson information
- ✅ Excel integration with color-coded status (Keldi/Kelmadi)
- ✅ FSM-based state management using aiogram 3.x
- ✅ Support for absence reporting with reason tracking
- ✅ Automated lesson counting and teacher list compilation

## Project Structure

```
Mars Intern/
├── src/
│   ├── __init__.py          # Package initializer
│   ├── main.py              # Bot entry point
│   ├── config.py            # Configuration settings
│   ├── states.py            # FSM states
│   ├── handlers.py          # Message handlers
│   ├── keyboards.py         # UI keyboards
│   ├── parser.py            # Report parsing logic
│   ├── excel_handler.py    # Excel file operations
│   └── interns.py           # List of interns
├── data/                    # Data storage (created automatically)
│   └── interns_reports.xlsx # Excel database (created on first run)
├── requirements.txt         # Python dependencies
├── .env.example             # Environment template
├── .env                     # Environment variables (create from .env.example)
└── README.md                # This file
```

## Installation

### 1. Clone and Setup
```bash
cd "Mars Intern"
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Bot Token
1. Create `.env` file from `.env.example`:
   ```bash
   cp .env.example .env
   ```
2. Get your bot token from [@BotFather](https://t.me/BotFather) on Telegram
3. Edit `.env` and replace `YOUR_BOT_TOKEN_HERE` with your token:
   ```
   BOT_TOKEN=123456789:ABCDefGHIjklmnoPQRStuvWXYZ
   ```

## Usage

### Starting the Bot
```bash
cd src
python main.py
```

The bot will start polling and be ready to receive messages.

### User Flow

1. **Start**: User sends `/start`
   - Bot shows main menu with "📚 Dars kiritish" button

2. **Select Intern**: User clicks the button
   - Bot shows list of all interns to select from

3. **Submit Report**: User selects their name
   - Bot sends report template
   - User fills and sends the template

4. **Confirmation**: Bot parses and shows summary
   - User confirms or rejects

5. **Save**: Report is saved to Excel with:
   - ✅ Green highlighting for "Keldi" (Present)
   - 🔴 Red highlighting for "Kelmadi" (Absent)

## Report Template

The template interns need to fill:

```
#hisobot
👤 Intern: [Your Name]
📅 Sana: DD.MM.YYYY

🕒 ISH VAQTI:
📥 Kelgan: HH:MM
📤 Ketgan: HH:MM
━━━━━━━━━━━━━━━━━━

📚 DARSLAR JADVALI:

🔹 Dars #1
┣ 👨‍🏫 Ustoz: Teacher Name
┣ 🚪 Xona: Room
┗ ⏰ Vaqt: HH:MM

🔹 Dars #2
┣ 👨‍🏫 Ustoz: Teacher Name
┣ 🚪 Xona: Room
┗ ⏰ Vaqt: HH:MM
```

## Excel Database

The `interns_reports.xlsx` file stores all attendance records with columns:

- **Ism Familiya** (Name): Intern name
- **[DD.MM.YYYY]** (Date columns): Each date gets its own column
  - "Keldi" entries = [Keldi] + lesson count + teacher names (Green)
  - "Kelmadi" entries = [Kelmadi] + absence reason (Red)

### Sample Excel Format

| Ism Familiya | 15.03.2026 | 16.03.2026 |
|---|---|---|
| Humoyun Jo'rayev | [Keldi] 2 dars<br/>Teacher1, Teacher2 | [Kelmadi] Kasallik |
| Aziz Nosirov | [Kelmadi] Shaxsiy ishlar | [Keldi] 3 dars<br/>Teacher1, Teacher2, Teacher3 |

## FSM States

The bot uses the following FSM states:

1. **selecting_name** - User selecting their name
2. **waiting_for_report** - Waiting for report template
3. **confirming_report** - Confirming parsed report
4. **waiting_for_absence_reason** - Getting absence reason

## Configuration

Edit `src/config.py` to customize:

- Bot token (via .env)
- Excel file location
- Button labels
- Messages and prompts
- Timezone
- Admin notifications (if needed)

## Troubleshooting

### Bot doesn't start
- Check if BOT_TOKEN is set in `.env`
- Verify token is valid (get from @BotFather)
- Check internet connection

### Excel file not created
- Ensure `data/` directory exists or will be created
- Check write permissions in project directory
- Install `openpyxl` and `pandas` properly

### Parsing errors
- Ensure report template format matches exactly
- Check that #hisobot starts the report
- Verify date format is DD.MM.YYYY
- Check time format is HH:MM

### Permission errors on Linux/Mac
```bash
chmod +x src/main.py
```

## Dependencies

- **aiogram** - Telegram bot API wrapper
- **python-dotenv** - Environment variable management
- **pandas** - Data manipulation
- **openpyxl** - Excel file handling
- **aiofiles** - Async file operations

## List of Interns

The bot tracks these 13 interns:

1. Humoyun Jo'rayev
2. Aziz Nosirov
3. Boxodirov Abdubosit
4. Baxromov Ibrohim
5. Tadjibayev Abdulaziz
6. Ahmadjonov Salohiddin
7. Rizayev Shodiyor
8. Madaminov Valijon
9. Murodjonov Ulugbek
10. Пулатов Билол
11. Суннатов Юсуф
12. Mansurov Abduraxim
13. Abduqaxxor Sunattilayev

## Future Enhancements

- [ ] Database support (MongoDB/PostgreSQL)
- [ ] Admin panel with statistics
- [ ] Automated daily reminders
- [ ] Google Sheets integration
- [ ] Weekly/monthly reports
- [ ] Teacher statistics
- [ ] Performance metrics

## License

Private project for Mars Internship

## Support

For issues or feature requests, contact the bot administrator.

---

**Version**: 1.0.0  
**Last Updated**: March 2026
# Mars-Intern-
# Mars-Intern
# Mars-Intern
# Mars-Intern
# Mars-intern
