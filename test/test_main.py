# test_main.py

import unittest
from unittest.mock import AsyncMock, patch, MagicMock
from openai_requests import ask_gpt_async  # Corrected import
from main import start_command, ask_gpt4o, user_caches  # Ensure correct import from project root
from aiogram.types import Message
import pytest
from aiogram import Bot, Dispatcher

class TestMain(unittest.IsolatedAsyncioTestCase):

    async def test_ask_gpt_async_success(self):
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = {
            "choices": [{
                "message": {
                    "content": "Test response"
                }
            }]
        }
        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_post.return_value.__aenter__.return_value = mock_response
            result = await ask_gpt_async(model="gpt-4o", messages=[])
            self.assertEqual(result, "Test response")

    async def test_start_command(self):
        mock_message = MagicMock(spec=Message)
        mock_message.from_user = MagicMock()
        mock_message.from_user.first_name = "TestUser"
        mock_message.reply = AsyncMock()

        await start_command(mock_message)

        mock_message.reply.assert_awaited_with("Բարև, TestUser! Ինչով կարող եմ օգնել?")

    async def test_ask_gpt4o_no_text(self):
        mock_message = MagicMock(spec=Message)
        mock_message.text = None
        mock_message.reply = AsyncMock()

        await ask_gpt4o(mock_message)
        mock_message.reply.assert_awaited_with("Ես կարող եմ մշակել միայն տեքստային հաղորդագրությունները: Խնդրում ենք ուղարկել только текст:")

    async def test_ask_gpt4o_start_command(self):
        mock_message = MagicMock(spec=Message)
        mock_message.from_user = MagicMock()
        mock_message.text = "start"
        mock_message.from_user.id = 123
        mock_message.from_user.first_name = "TestUser"
        mock_message.reply = AsyncMock()
        mock_message.bot.send_chat_action = AsyncMock()

        with patch('main.ask_gpt_async', return_value=AsyncMock()):
            await ask_gpt4o(mock_message)

            mock_message.reply.assert_awaited_with("Բարև, TestUser! Ինչով կարող եմ օգնել?")
            self.assertIn(123, user_caches)

@patch('main.start_command')
@patch('aiogram.Bot')
@patch('aiogram.Dispatcher')
@pytest.mark.asyncio
async def test_start_command_pytest(mock_dispatcher, mock_bot, mock_start_command):
    message = AsyncMock()
        message.from_user.first_name = "TestUser"
    message.from_user.first_name = "TestUser"
    message.reply = AsyncMock()
    
        await start_command(message)
        message.reply.assert_awaited_with("Բարև, TestUser! Ինչով կարող եմ օգնել?")

if __name__ == '__main__':
    unittest.main()
    await start_command(message)
    message.reply.assert_awaited_with("Բարև, TestUser! Ինչով կարող եմ օգնել?")

if __name__ == '__main__':
    unittest.main()
        message.reply = AsyncMock()
        