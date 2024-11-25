import aiosqlite
import datetime
import time

DB_FILE = "requests.db"

# Инициализация базы данных
async def init_db():
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS user_requests (
                user_id INTEGER PRIMARY KEY,
                request_count INTEGER DEFAULT 0,
                last_request_timestamp REAL,
                hour_of_request TEXT DEFAULT NULL,
                language_code TEXT DEFAULT 'en'  # Новый столбец для языка пользователя
            )
        """)
        await db.commit()

# Функция для получения языка пользователя из базы данных
async def fetch_user_language_from_db(user_id):
    async with aiosqlite.connect(DB_FILE) as db:
        async with db.execute("""
            SELECT language_code FROM user_requests WHERE user_id = ?
        """, (user_id,)) as cursor:
            row = await cursor.fetchone()
            if row:
                return row[0]
            else:
                # User not found, return None
                return None

# Функция для установки языка пользователя в базе данных
async def set_user_language_in_db(user_id, language_code):
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute("""
            INSERT INTO user_requests (user_id, language_code, last_request_timestamp)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET language_code = ?, last_request_timestamp = ?
        """, (user_id, language_code, time.time(), language_code, time.time()))
        await db.commit()

# Расчет доступных запросов с учетом времени восстановления
async def calculate_available_requests(user_id):
    async with aiosqlite.connect(DB_FILE) as db:
        async with db.execute("""
            SELECT request_count, last_request_timestamp
            FROM user_requests
            WHERE user_id = ?
        """, (user_id,)) as cursor:
            row = await cursor.fetchone()

            # Если пользователя нет в базе, добавляем его
            if not row:
                await db.execute("""
                    INSERT INTO user_requests (user_id, request_count, last_request_timestamp)
                    VALUES (?, 0, ?)
                """, (user_id, time.time()))
                await db.commit()
                return 20  # Новый пользователь получает полный лимит

            request_count, last_request_timestamp = row

            # Рассчитываем время, прошедшее с момента последнего запроса
            elapsed_time = time.time() - last_request_timestamp

            # Если прошло более 24 часов, сбрасываем запросы
            if (elapsed_time > 24 * 60 * 60):
                return 20

            # Рассчитываем восстановленные запросы
            restored_requests = int(elapsed_time // (72 * 60))  # Каждые 72 минуты восстанавливается 1 запрос

            # Общий доступный лимит
            available_requests = min(20, 20 - request_count + restored_requests)
            return available_requests

# Проверка, может ли пользователь сделать запрос
async def can_make_request(user_id):
    available_requests = await calculate_available_requests(user_id)
    return available_requests > 0

# Обновление данных после запроса
async def update_request_data(user_id):
    async with aiosqlite.connect(DB_FILE) as db:
        async with db.execute("""
            SELECT request_count, last_request_timestamp
            FROM user_requests
            WHERE user_id = ?
        """, (user_id,)) as cursor:
            row = await cursor.fetchone()
            if row:
                request_count, last_request_timestamp = row
                elapsed_time = time.time() - last_request_timestamp
                restored_requests = int(elapsed_time // (72 * 60))

                # Обновляем счетчик с учетом восстановленных запросов
                new_request_count = max(0, request_count - restored_requests) + 1

                # Получаем текущее время в формате HH:MM
                current_time_formatted = datetime.datetime.now().strftime("%H:%M")

                # Обновляем запись
                await db.execute("""
                    UPDATE user_requests
                    SET request_count = ?, last_request_timestamp = ?, hour_of_request = ?
                    WHERE user_id = ?
                """, (new_request_count, time.time(), current_time_formatted, user_id))
                await db.commit()

# Получение количества запросов (не используется для расчета лимита)
async def get_request_count(user_id):
    async with aiosqlite.connect(DB_FILE) as db:
        async with db.execute("""
            SELECT request_count
            FROM user_requests
            WHERE user_id = ?
        """, (user_id,)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else 0