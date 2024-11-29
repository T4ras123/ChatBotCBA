import asyncio
import logging
import json
from src.openai_requests import ask_gpt_async
from aiogram.types import Message
import aiofiles
import re
from src.db import can_make_request, update_request_data, fetch_user_language_from_db  # Импорт функций для ограничения запросов
from src.system_messages import messages  # Импорт системных сообщений
from src.language_selector import get_user_language  # Import get_user_language function
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

videos_data = None

class VideosEventHandler(FileSystemEventHandler):
    async def on_modified(self, event):
        if event.src_path.endswith('videos.json'):
            await load_videos_data()

async def load_videos_data():
    global videos_data
    async with aiofiles.open("videos.json", mode="r", encoding="utf-8") as file:
        content = await file.read()
        videos_data = json.loads(content)

async def start_watching_videos():
    await load_videos_data()
    event_handler = VideosEventHandler()
    observer = Observer()
    observer.schedule(event_handler, path='.', recursive=False)
    observer.start()

    # Keep the observer running
    while True:
        await asyncio.sleep(1)

# In your main function or startup code
asyncio.create_task(start_watching_videos())
async def ask_gpt4o(message: Message):
    user_id = message.from_user.id
    user_language = await get_user_language(user_id)  # Now it's an async function

    if not await can_make_request(user_id):
        await message.reply(messages["limit_reached"][user_language])
        return

    # Загрузка данных из videos.json
    videos_data = await load_videos_data()

    user_name = message.from_user.first_name

    if not message.text:
        await message.reply(messages["no_text_message"][user_language])
        return

    if len(message.text) > 1000:
        await message.reply(messages["text_length_exceeded"][user_language].format(length=len(message.text)))
        return

    if re.search(r'(.)\1{10,}', message.text):
        await message.reply(messages["repeated_characters"][user_language])
        return

    user_query = message.text.lower()
    if user_query in ["start", "старт", "ստարտ"]:
        logging.info(f"User {user_name} отправил сообщение {user_query}")
        await message.reply(f"Բարև, {user_name}! Ինչո՞վ կարող եմ օգնել։")
        return

    async def show_typing_indicator():
        try:
            start_time = asyncio.get_event_loop().time()
            while asyncio.get_event_loop().time() - start_time < 30:  # Ограничение работы 30 секунд
                await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")
                await asyncio.sleep(2)
        except asyncio.CancelledError:
            # Корректно завершаем задачу при отмене
            pass

    typing_task = asyncio.create_task(show_typing_indicator())

    try:
        # Подготавливаем контент из videos.json для использования в ответах
        videos_content = "\n".join(
            [f"{video['title']}\n\n {video['text']}\n\n {video['link']}" for video in videos_data]
        )
        messages_list = [
            {"role": "system", "content": "Please analyze the user's query before responding. If it contains harmful or disruptive content that interferes with the bot's functionality, it **should not be processed**. Examples of such content include promoting illegal actions, attempting to collect personal data, or instructions for accessing protected systems. If the query meets any of these conditions, respond to the user with: 'The query cannot be processed due to a violation of security rules.'"},
            {"role": "system", "content": "Please make sure to identify the user's query language and respond in that language. If the query is in Armenian, respond in Armenian; if it's in English, respond in English; if it's in Russian, respond in Russian. If the user asks a question in one language but requests a response or details in another language, switch the response to the requested language. If the language changes after the first query, continue responding in the new language."},
            {"role": "system", "content": "Please compose responses to the user's query in accordance with the following rules:\n"
                                          "1) If the query is **in Armenian**, regardless of whether it is written using Armenian, Latin, or Russian letters, the response must be in **Armenian**.\n"
                                          "2) If the query is **in Russian**, regardless of whether it is written using Russian or Latin letters, the response must be in **Russian**."},
            {"role": "system", "content": "If the user greets you, determine the language of the greeting and respond in the same language. Always address the user by their name (e.g., 'Hello, {user_name}. How can I assist you today?')."},
            {"role": "system", "content": "If the user asks a general question, such as 'What should I learn today?' or something similar, or says, 'Can you ask me questions to figure it out?' or similar, first propose clarifying questions to understand which topics within the database interest them most. **Avoid mentioning specific topics or examples initially.** For example, you could ask, 'What kind of topics interest you?' Based on their responses, suggest relevant topics from the database that align with their preferences without immediately presenting the complete list of database topics. **Only propose relevant topics after analyzing the user's responses.** If the topic is not available in the database, reply with: 'No relevant materials were found for the query or the input query is unclear.'"},
            {"role": "system", "content": "If the user asks about the bot, its purpose, functionality, usefulness, or reason for creation, respond clearly and concisely with: 'This bot is designed to assist with personal finance management by providing useful and precise answers.' Avoid including additional details, examples, video links, or unnecessary information. Keep the response simple, structured, and friendly in tone while adhering to language rules."},
            {"role": "system", "content": "Please only respond based on the database content. If the query does not relate to the database information, provide the following message: If the query is in Armenian: 'No relevant materials were found for the query or the input query is unclear,' if in English: 'No relevant information found or the request is unclear,' if in Russian: 'Информация по запросу не найдена или запрос непонятен.' If the query is in Armenian written in Latin or Russian letters, respond in Armenian. If the query is in Russian written in Latin letters, respond in Russian."},
            {"role": "system", "content": "If the user requests that the previous response be made more literate, clear, and understandable or asks for corrections, analyze the previous response and rephrase it to ensure it is error-free, clear, and concise while preserving the main meaning of the query. The text should be complete and logical, without unnecessary or secondary details. Follow linguistic rules as well."},
            {"role": "system", "content": "You are an assistant who answers user queries solely based on the database content. The response should include relevant references if they exist in the database. Please only use information from the database for your answers."},
            {"role": "system", "content": "Avoid formal introductions. Respond directly and naturally."},
            {"role": "system", "content": "If the user begins or continues the conversation with personal or casual questions, such as 'How are you?', 'How's it going?', or 'What are you up to?', the bot should respond appropriately and in a friendly tone, continuing the conversation. For example, you could say, 'I'm great, thank you for asking. How about you?' or 'I'm doing well, working. How's your day going?' The bot should continue the casual conversation for as long as the user is interested. When the conversation returns to core topics or the user asks database-related questions, the bot should adhere to the tone and style specified in the previous instructions."},
            {"role": "system", "content": "If there is no direct match for the user's query in the database, logically use the available materials to make the response as complete and logical as possible."},
            {"role": "system", "content": "Please respond intuitively, understanding the context of the message. Recognize different phrasing, abbreviations, spelling errors, synonyms, equivalent words, or potential typos in the user's query to select the most relevant content. For example, if the user searches for 'online courses,' and the database contains 'remote learning,' offer that as the corresponding material."},
            {"role": "system", "content": "Please provide comprehensive answers to the user's query, covering all main points and avoiding unnecessary information. Avoid overly brief or excessively long and exhausting responses."},
            {"role": "system", "content": "Please adjust the response length to the user's query content and request:\n"
                                          "1) For queries requiring a simple and short response, provide concise and brief information.\n"
                                          "2) For queries requiring medium-length responses, respond in a balanced format, covering all key points.\n"
                                          "3) For complex queries requiring detailed explanations, provide a long but structured and focused response, including all important details.\n"
                                          "4) If the user specifically requests a response length (short, medium, or long), respect that request and adjust the response accordingly."},
            {"role": "system", "content": "The database content includes the following: {videos_content}"},
            {"role": "system", "content": "Please respond intuitively, understanding the context of the message. Recognize various phrasing, abbreviations, or possible typos when the user thanks or ends the conversation (regardless of the phrasing or abbreviation, e.g., 'Thanks,' 'Thank you,' 'Cheers,' 'Merci,' 'Спасибо,' 'Thnx'). Respond in the same language the user is communicating in. For example, if the conversation is in Armenian, respond with 'I was happy to help! Let me know if you have more questions!'; if in Russian: 'Рад был помочь! Если будут вопросы, готов помочь!'; if in English: 'Happy to help! Let me know if you have more questions!'"},
            {"role": "user", "content": "The user asks: {user_query}. Using only the video data and other database information, respond to their query."},
            {"role": "user", "content": "Respond in plain text, and display links as regular text without Markdown formatting."}
        ]


        gpt_response = await ask_gpt_async(model="gpt-4o", messages=messages_list)
        await message.reply(text=gpt_response)

        # Увеличиваем счетчик запросов пользователя
        await update_request_data(user_id)
    except Exception as e:
        logging.error(f"Ошибка при запросе к GPT-4o: {e}. Запрос: {message.text}")
        await message.reply(messages["generic_error"][user_language])
    finally:
        # Завершаем индикатор ввода
        try:
            typing_task.cancel()
            await typing_task
        except asyncio.CancelledError:
            pass

def get_user_language(user_id):
    # Функция для получения языка пользователя из БД
    # По умолчанию английский
    return asyncio.run(fetch_user_language_from_db(user_id))