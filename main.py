import logging
from config import token
from aiogram import Bot, Dispatcher, Router
from aiogram.client.bot import DefaultBotProperties
from aiogram.filters import Command
from aiogram.types import Message
from message_handler import ask_gpt4o  # Импортируем обработчик сообщений
from language_selector import create_language_keyboard, handle_language_selection  # Новый модуль для выбора языка
from db import init_db, fetch_user_language_from_db  # Инициализация базы данных
from system_messages import messages  # Импорт системных сообщений
import asyncio

# Настройка логирования
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(уровень)s - %(сообщение)s")

# Создаем роутер для обработки команд и сообщений
router = Router()


@router.message(Command(commands=["start"]))
async def start_command(message: Message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    user_language = await get_user_language(user_id)  # Функция для получения языка пользователя из БД

    logging.info(f"User {user_name} вызвал команду /start")

    # Приветствие на основании языка пользователя или всех языках, если язык не выбран
    if user_language in ["hy", "ru", "en"]:
        greeting = messages["greeting"][user_language].format(user_name=user_name)
        await message.reply(greeting)
    else:
        # Если язык не выбран, отправляем мультилингвальное приветствие
        await message.reply(
            messages["greeting"]["hy"].format(user_name=user_name) + "\n\n" +
            messages["greeting"]["ru"].format(user_name=user_name) + "\n\n" +
            messages["greeting"]["en"].format(user_name=user_name)
        )

    # Сообщение с выбором языка
    await message.reply(
        messages["language_selection_prompt"]["hy"] + "\n\n" +
        messages["language_selection_prompt"]["ru"] + "\n\n" +
        messages["language_selection_prompt"]["en"],
        reply_markup=create_language_keyboard()  # Клавиатура из language_selector.py
    )


# Подключаем обработчик текстовых сообщений
router.message()(ask_gpt4o)

# Подключаем обработчик кнопок из language_selector.py
router.callback_query()(handle_language_selection)


async def main():
    # Инициализация базы данных
    await init_db()

    # Создаем бота и диспетчер
    bot = Bot(token, default=DefaultBotProperties(parse_mode='HTML'))
    dp = Dispatcher()
    dp.include_router(router)

    # Удаляем старые вебхуки и запускаем бота
    await bot.delete_webhook(drop_pending_updates=True)
    logging.info("Бот успешно запущен и готов к обработке сообщений.")
    await dp.start_polling(bot)


async def get_user_language(user_id):
    # Функция для получения языка пользователя из БД
    # По умолчанию английский
    return await fetch_user_language_from_db(user_id)


if __name__ == '__main__':
    asyncio.run(main())