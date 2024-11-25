import logging
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from system_messages import messages  # Import system messages
from db import set_user_language_in_db, fetch_user_language_from_db  # Import database functions

# Словарь для хранения выбранного языка пользователей
user_languages = {}

# ...existing code...

# Функция для создания клавиатуры выбора языка
def create_language_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Հայերեն 🇦🇲", callback_data="lang_arm")],
        [InlineKeyboardButton(text="Русский 🇷🇺", callback_data="lang_rus")],
        [InlineKeyboardButton(text="English 🇺🇸", callback_data="lang_eng")]
    ])
    return keyboard

# Обработчик нажатий на кнопки
async def handle_language_selection(callback: CallbackQuery):
    user_id = callback.from_user.id
    data = callback.data

    # Определяем выбранный язык
    if data == "lang_arm":
        selected_language = "hy"
        language_name = "Հայերեն"
    elif data == "lang_rus":
        selected_language = "ru"
        language_name = "Русский"
    elif data == "lang_eng":
        selected_language = "en"
        language_name = "English"
    else:
        logging.warning(f"Неизвестная callback_data: {data}")
        return

    user_languages[user_id] = selected_language

    # Сохраняем язык пользователя в базе данных
    await set_user_language_in_db(user_id, selected_language)

    # Получаем текст уведомления на выбранном языке
    notification_text = messages["language_selection_confirmation"][selected_language].format(language_name=language_name)

    # Ответ на выбор языка
    await callback.message.answer(notification_text)

    # Уведомление Telegram о том, что callback обработан
    await callback.answer()

# Функция для получения языка пользователя (по умолчанию английский)
async def get_user_language(user_id):
    language = await fetch_user_language_from_db(user_id)
    return language or "en"