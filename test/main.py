import logging
from config import token
from aiogram import Bot, Dispatcher, Router
from aiogram.client.bot import DefaultBotProperties
from aiogram.filters import Command
from aiogram.types import Message
from message_handler import ask_gpt4o  # Импортируем новый обработчик
import asyncio

logging.basicConfig(level=logging.INFO)
router = Router()

@router.message(Command(commands=["start"]))
async def start_command(message: Message):
    user_name = message.from_user.first_name
    logging.info(f"User {user_name} вызвал команду /start")
    await message.reply(f"Բարև, {user_name}! Ինչով կարող եմ օգնել?")

# Подключаем обработчик текстовых сообщений
router.message()(ask_gpt4o)

async def main():
    bot = Bot(token, default=DefaultBotProperties(parse_mode='HTML'))
    dp = Dispatcher()
    dp.include_router(router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
