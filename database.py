import asyncpg
from datetime import datetime
from typing import Optional
import logging

# Database connection pool
pool: Optional[asyncpg.Pool] = None

async def init_db():
    """Initialize database connection pool"""
    global pool
    pool = await asyncpg.create_pool(
        user='postgres',
        password='your_password',  # Move to config
        database='your_database',
        host='localhost'
    )

    # Create tables if they don't exist
    async with pool.acquire() as conn:
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS daily_usage (
                user_id BIGINT REFERENCES users(id),
                date DATE NOT NULL,
                usage_count INTEGER DEFAULT 0,
                PRIMARY KEY (user_id, date)
            )
        ''')

async def is_allowed_message(user_id: int) -> bool:
    """Check if user hasn't exceeded daily limit"""
    if not pool:
        await init_db()
        
    async with pool.acquire() as conn:
        try:
            today = datetime.today().date()
            
            # Get current usage
            row = await conn.fetchrow(
                '''
                SELECT usage_count 
                FROM daily_usage 
                WHERE user_id = $1 AND date = $2
                ''',
                user_id, today
            )

            if row and row['usage_count'] >= 50:
                return False

            # Update or insert usage count
            if row:
                await conn.execute(
                    '''
                    UPDATE daily_usage 
                    SET usage_count = usage_count + 1 
                    WHERE user_id = $1 AND date = $2
                    ''',
                    user_id, today
                )
            else:
                await conn.execute(
                    '''
                    INSERT INTO daily_usage (user_id, date, usage_count) 
                    VALUES ($1, $2, 1)
                    ''',
                    user_id, today
                )
            
            return True
            
        except Exception as e:
            logging.error(f"Database error: {e}")
            return False

# Clean up connection pool on shutdown
async def cleanup():
    if pool:
        await pool.close()