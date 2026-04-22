"""
SQLite Database module for Mars Intern Bot
"""
import sqlite3
from pathlib import Path
from datetime import date, datetime
from typing import Dict, List, Optional, Tuple
from config import BASE_DIR
from interns import INTERNS

DATABASE_FILE = BASE_DIR / "data" / "mars_intern.db"


class Database:
    """SQLite database handler"""
    
    def __init__(self):
        self.db_file = DATABASE_FILE
        self.db_file.parent.mkdir(parents=True, exist_ok=True)
        self.create_tables()
    
    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row
        return conn

    def ensure_column(self, table_name: str, column_name: str, column_definition: str):
        """Add column to table if it does not exist yet"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(f"PRAGMA table_info({table_name})")
            existing_columns = {row["name"] for row in cursor.fetchall()}

            if column_name not in existing_columns:
                cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_definition}")
                conn.commit()
        finally:
            conn.close()
    
    def create_tables(self):
        """Create all required tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Reports table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                intern_name TEXT NOT NULL,
                report_date DATE NOT NULL,
                arrival_time TEXT,
                departure_time TEXT,
                lesson_count INTEGER DEFAULT 0,
                teachers TEXT,
                status TEXT DEFAULT 'Keldi',
                absence_reason TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(intern_name, report_date)
            )
        ''')
        
        # Admin users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS admin_users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE NOT NULL,
                username TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Logs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                action TEXT,
                details TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Submitted reasons table - store reasons entered by interns/users
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS submitted_reasons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                username TEXT,
                intern_name TEXT,
                reason_type TEXT NOT NULL,
                reason_text TEXT NOT NULL,
                reason_date DATE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Lessons table - store individual lessons
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS lessons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                report_id INTEGER,
                intern_name TEXT NOT NULL,
                lesson_date DATE NOT NULL,
                lesson_number INTEGER,
                teacher_name TEXT NOT NULL,
                room TEXT,
                lesson_time TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(report_id) REFERENCES reports(id)
            )
        ''')
        
        # Work sessions table - track intern work time
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS work_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                intern_name TEXT NOT NULL,
                work_date DATE NOT NULL,
                start_time TIMESTAMP,
                end_time TIMESTAMP,
                duration_minutes INTEGER,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(intern_name, work_date, start_time)
            )
        ''')

        conn.commit()
        conn.close()

        self.ensure_column("reports", "user_id", "INTEGER")
        self.ensure_column("reports", "username", "TEXT")
        self.ensure_column("reports", "raw_text", "TEXT")
        self.ensure_column("work_sessions", "user_id", "INTEGER")
        self.ensure_column("work_sessions", "username", "TEXT")
        self.ensure_column("work_sessions", "ended_by_user_id", "INTEGER")
        self.ensure_column("work_sessions", "ended_by_username", "TEXT")
    
    # REPORTS OPERATIONS
    
    def add_report(self, data: Dict) -> bool:
        """Add or update a report"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Convert date to string if it's a date object
            report_date = data['date']
            if hasattr(report_date, 'strftime'):
                report_date = report_date.strftime('%Y-%m-%d')
            
            # First, get report ID if it exists
            cursor.execute('''
                SELECT id FROM reports 
                WHERE intern_name = ? AND report_date = ?
            ''', (data['intern_name'], report_date))
            
            report_result = cursor.fetchone()
            if report_result:
                report_id = report_result['id']
            else:
                report_id = None
            
            # Delete existing report and lessons
            if report_id:
                cursor.execute('DELETE FROM lessons WHERE report_id = ?', (report_id,))
                cursor.execute('DELETE FROM reports WHERE id = ?', (report_id,))
            
            # Insert new report
            cursor.execute('''
                INSERT INTO reports 
                (intern_name, report_date, arrival_time, departure_time, 
                 lesson_count, teachers, status, absence_reason, user_id, username, raw_text)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data['intern_name'],
                report_date,
                data.get('arrival_time', ''),
                data.get('departure_time', ''),
                len(data.get('lessons', [])),
                ', '.join([lesson['teacher'] for lesson in data.get('lessons', [])]),
                data.get('status', 'Keldi'),
                data.get('absence_reason', ''),
                data.get('user_id'),
                data.get('username'),
                data.get('raw_text', '')
            ))
            
            # Get the new report ID
            report_id = cursor.lastrowid
            
            print(f"📝 Report ID: {report_id}, Lessons: {len(data.get('lessons', []))}")
            
            # Add individual lessons
            for lesson in data.get('lessons', []):
                print(f"   ➕ Adding lesson: {lesson.get('teacher', '')} at {lesson.get('time', '')}")
                cursor.execute('''
                    INSERT INTO lessons 
                    (report_id, intern_name, lesson_date, lesson_number, 
                     teacher_name, room, lesson_time)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    report_id,
                    data['intern_name'],
                    report_date,
                    lesson.get('number', 0),
                    lesson.get('teacher', ''),
                    lesson.get('room', ''),
                    lesson.get('time', '')
                ))
            
            conn.commit()
            print(f"✅ Report saved: {data['intern_name']} - {report_date}")
            return True
        except Exception as e:
            print(f"❌ Error adding report: {e}")
            return False
        finally:
            conn.close()
    
    def get_report(self, intern_name: str, report_date: date) -> Optional[Dict]:
        """Get a specific report"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM reports 
            WHERE intern_name = ? AND report_date = ?
        ''', (intern_name, report_date))
        
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    
    def get_reports_by_date(self, report_date: date) -> List[Dict]:
        """Get all reports for a specific date"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM reports 
            WHERE report_date = ?
            ORDER BY intern_name ASC
        ''', (report_date,))
        
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def get_reports_by_intern(self, intern_name: str, days: int = 30) -> List[Dict]:
        """Get reports for specific intern (last N days)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM reports 
            WHERE intern_name = ? 
            AND report_date >= date('now', '-' || ? || ' days')
            ORDER BY report_date DESC
        ''', (intern_name, days))
        
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def get_attendance_summary(self, report_date: date = None) -> Dict:
        """Get attendance summary for a date"""
        if report_date is None:
            report_date = date.today()
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get summary
        cursor.execute('''
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN status = 'Keldi' THEN 1 ELSE 0 END) as present,
                SUM(CASE WHEN status = 'Kelmadi' THEN 1 ELSE 0 END) as absent
            FROM reports 
            WHERE report_date = ?
        ''', (report_date,))
        
        result = cursor.fetchone()
        conn.close()
        
        return {
            'date': report_date,
            'total': result['total'] or 0,
            'present': result['present'] or 0,
            'absent': result['absent'] or 0,
            'not_reported': len(INTERNS) - (result['total'] or 0)
        }

    def auto_mark_absent_for_date(
        self,
        report_date: date,
        reason: str = "Kun yakunigacha hisobot yubormadi"
    ) -> List[str]:
        """Mark missing interns as absent for the given date"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('''
                SELECT intern_name FROM reports
                WHERE report_date = ?
            ''', (report_date,))
            reported_interns = {row['intern_name'] for row in cursor.fetchall()}
            missing_interns = [intern for intern in INTERNS if intern not in reported_interns]

            for intern_name in missing_interns:
                cursor.execute('''
                    INSERT INTO reports
                    (intern_name, report_date, arrival_time, departure_time,
                     lesson_count, teachers, status, absence_reason)
                    VALUES (?, ?, '', '', 0, '', 'Kelmadi', ?)
                ''', (intern_name, report_date, reason))

            conn.commit()
            return missing_interns
        except Exception as e:
            print(f"Error auto marking absences: {e}")
            return []
        finally:
            conn.close()
    
    def delete_report(self, intern_name: str, report_date: date) -> bool:
        """Delete a report"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                DELETE FROM reports 
                WHERE intern_name = ? AND report_date = ?
            ''', (intern_name, report_date))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error deleting report: {e}")
            return False
        finally:
            conn.close()
    
    # LESSONS OPERATIONS
    
    def get_all_lessons(self, days: int = 30) -> List[Dict]:
        """Get all lessons from last N days"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM lessons 
            WHERE lesson_date >= date('now', '-' || ? || ' days')
            ORDER BY lesson_date DESC, intern_name ASC, lesson_number ASC
        ''', (days,))
        
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def get_lessons_by_intern(self, intern_name: str, days: int = 30) -> List[Dict]:
        """Get lessons for specific intern"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM lessons 
            WHERE intern_name = ? 
            AND lesson_date >= date('now', '-' || ? || ' days')
            ORDER BY lesson_date DESC, lesson_number ASC
        ''', (intern_name, days))
        
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def get_lessons_by_date(self, lesson_date: date) -> List[Dict]:
        """Get all lessons for a specific date"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM lessons 
            WHERE lesson_date = ?
            ORDER BY intern_name ASC, lesson_number ASC
        ''', (lesson_date,))
        
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    # ADMIN OPERATIONS
    
    def add_admin(self, user_id: int, username: str = None) -> bool:
        """Add admin user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO admin_users (user_id, username)
                VALUES (?, ?)
            ''', (user_id, username))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error adding admin: {e}")
            return False
        finally:
            conn.close()
    
    def is_admin(self, user_id: int) -> bool:
        """Check if user is admin"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id FROM admin_users WHERE user_id = ?
        ''', (user_id,))
        
        result = cursor.fetchone()
        conn.close()
        return result is not None
    
    def get_admins(self) -> List[Dict]:
        """Get all admin users"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM admin_users ORDER BY created_at DESC')
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def remove_admin(self, user_id: int) -> bool:
        """Remove admin user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('DELETE FROM admin_users WHERE user_id = ?', (user_id,))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error removing admin: {e}")
            return False
        finally:
            conn.close()
    
    # LOGS OPERATIONS
    
    def add_log(self, user_id: int, action: str, details: str = None) -> bool:
        """Add activity log"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO logs (user_id, action, details)
                VALUES (?, ?, ?)
            ''', (user_id, action, details))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error adding log: {e}")
            return False
        finally:
            conn.close()

    def add_submitted_reason(
        self,
        user_id: int,
        username: str,
        reason_type: str,
        reason_text: str,
        reason_date: date = None,
        intern_name: str = None
    ) -> bool:
        """Save a user-submitted reason to database"""
        if reason_date is None:
            reason_date = date.today()

        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('''
                INSERT INTO submitted_reasons
                (user_id, username, intern_name, reason_type, reason_text, reason_date)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, username, intern_name, reason_type, reason_text, reason_date))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error adding submitted reason: {e}")
            return False
        finally:
            conn.close()

    def get_submitted_reasons(self, days: int = 30) -> List[Dict]:
        """Get submitted reasons from last N days"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM submitted_reasons
            WHERE reason_date >= date('now', '-' || ? || ' days')
            ORDER BY created_at DESC
        ''', (days,))

        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def get_logs(self, limit: int = 100) -> List[Dict]:
        """Get recent logs"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM logs 
            ORDER BY created_at DESC 
            LIMIT ?
        ''', (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    # WORK SESSION OPERATIONS
    
    def start_work_session(self, intern_name: str, user_id: int = None, username: str = None) -> bool:
        """Start work session for intern"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Check if there's already an active session
            cursor.execute('''
                SELECT id FROM work_sessions 
                WHERE intern_name = ? AND work_date = ? AND status = 'active'
            ''', (intern_name, date.today()))
            
            if cursor.fetchone():
                return False  # Already has active session
            
            cursor.execute('''
                INSERT INTO work_sessions 
                (intern_name, work_date, start_time, status, user_id, username)
                VALUES (?, ?, ?, 'active', ?, ?)
            ''', (intern_name, date.today(), datetime.now(), user_id, username))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Error starting work session: {e}")
            return False
        finally:
            conn.close()
    
    def end_work_session(self, intern_name: str, ended_by_user_id: int = None, ended_by_username: str = None) -> bool:
        """End work session for intern"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Get active session
            cursor.execute('''
                SELECT id, start_time FROM work_sessions 
                WHERE intern_name = ? AND work_date = ? AND status = 'active'
            ''', (intern_name, date.today()))
            
            session = cursor.fetchone()
            if not session:
                return False  # No active session
            
            # Calculate duration
            start_time = datetime.fromisoformat(session['start_time'])
            end_time = datetime.now()
            duration_minutes = int((end_time - start_time).total_seconds() / 60)
            
            # Update session
            cursor.execute('''
                UPDATE work_sessions 
                SET end_time = ?, duration_minutes = ?, status = 'completed',
                    ended_by_user_id = ?, ended_by_username = ?
                WHERE id = ?
            ''', (end_time, duration_minutes, ended_by_user_id, ended_by_username, session['id']))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Error ending work session: {e}")
            return False
        finally:
            conn.close()
    
    def get_work_session(self, intern_name: str, work_date: date = None) -> Optional[Dict]:
        """Get active or today's work session"""
        if work_date is None:
            work_date = date.today()
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM work_sessions 
            WHERE intern_name = ? AND work_date = ? AND status = 'active'
        ''', (intern_name, work_date))
        
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    
    def get_work_sessions_by_date(self, work_date: date) -> List[Dict]:
        """Get all work sessions for a specific date"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM work_sessions 
            WHERE work_date = ?
            ORDER BY intern_name ASC, start_time ASC
        ''', (work_date,))
        
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def get_work_sessions_by_intern(self, intern_name: str, days: int = 30) -> List[Dict]:
        """Get work sessions for specific intern (last N days)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM work_sessions 
            WHERE intern_name = ? 
            AND work_date >= date('now', '-' || ? || ' days')
            ORDER BY work_date DESC, start_time DESC
        ''', (intern_name, days))
        
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def get_work_duration_today(self, intern_name: str) -> int:
        """Get total work duration for today in minutes"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT SUM(duration_minutes) as total 
            FROM work_sessions 
            WHERE intern_name = ? AND work_date = ? AND status = 'completed'
        ''', (intern_name, date.today()))
        
        row = cursor.fetchone()
        conn.close()
        
        return row['total'] or 0 if row else 0


# Global database instance
db = Database()
