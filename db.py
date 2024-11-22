import aiosqlite
from datetime import datetime
import logging

# Database file path
db_path = 'request.db'

async def init_db():
    """Initialize the SQLite database"""
    async with aiosqlite.connect(db_path) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT
            )
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS daily_usage (
                user_id INTEGER,
                date DATE NOT NULL,
                usage_count INTEGER DEFAULT 0,
                PRIMARY KEY (user_id, date),
            )
        ''')
        await db.commit()

async def is_allowed_message(user_id: int) -> bool:
    """Check if user hasn't exceeded daily limit"""
    try:
        async with aiosqlite.connect(db_path) as db:
            today = datetime.today().date()

            # Get current usage
            cursor = await db.execute(
                '''
                SELECT usage_count 
                FROM daily_usage 
                WHERE user_id = ? AND date = ?
                ''',
                (user_id, today)
            )
            row = await cursor.fetchone()

            if row and row[0] >= 20:
                return False

            # Update or insert usage count
            if row:
                await db.execute(
                    '''
                    UPDATE daily_usage 
                    SET usage_count = usage_count + 1 
                    WHERE user_id = ? AND date = ?
                    ''',
                    (user_id, today)
                )
            else:
                await db.execute(
                    '''
                    INSERT INTO daily_usage (user_id, date, usage_count) 
                    VALUES (?, ?, 1)
                    ''',
                    (user_id, today)
                )
            await db.commit()
            return True

    except Exception as e:
        logging.error(f"Database error: {e}")
        return False

async def add_user(user_id: int, username: str) -> bool:
    """Add new user to database"""
    try:
        async with aiosqlite.connect(db_path) as db:
            await db.execute(
                '''
                INSERT INTO users (id, username) 
                VALUES (?, ?)
                ON CONFLICT(id) DO UPDATE SET username=excluded.username
                ''',
                (user_id, username)
            )
            await db.commit()
            return True
    except Exception as e:
        logging.error(f"Error adding user: {e}")
        return False
