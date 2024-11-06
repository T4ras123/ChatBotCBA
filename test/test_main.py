# test_main.py

import unittest
from unittest.mock import AsyncMock, patch, MagicMock
from main import ask_gpt_async, ask_gpt4o, start_command, user_caches
from aiogram.types import Message

class TestMain(unittest.IsolatedAsyncioTestCase):
    async def test_ask_gpt_async_success(self):
        async def mock_post(*args, **kwargs):
            response = AsyncMock()
            response.status = 200
            response.json = AsyncMock(return_value={
                "choices": [{
                    "message": {
                        "content": "Test response"
                    }
                }]
            })
            return response

        with patch('aiohttp.ClientSession.post', new=mock_post):
            result = await ask_gpt_async(model="gpt-4", messages=[])
            self.assertEqual(result, "Test response")

    async def test_ask_gpt_async_error(self):
        async def mock_post(*args, **kwargs):
            response = AsyncMock()
            response.status = 400
            response.text = AsyncMock(return_value="Bad Request")
            return response

        with patch('aiohttp.ClientSession.post', new=mock_post):
            with self.assertRaises(Exception) as context:
                await ask_gpt_async(model="gpt-4", messages=[])
            self.assertIn("Error 400", str(context.exception))

    async def test_start_command(self):
        message = MagicMock(spec=Message)
        message.from_user.first_name = "TestUser"
        message.reply = AsyncMock()

        await start_command(message)
        message.reply.assert_called_once_with("Բարև, TestUser! Ինչով կարող եմ օգնել?")

    async def test_ask_gpt4o_no_text(self):
        message = MagicMock(spec=Message)
        message.text = None
        message.reply = AsyncMock()

        await ask_gpt4o(message)
        message.reply.assert_called_once_with("Ես կարող եմ մշակել միայն տեքստային հաղորդագրությունները: Խնդրում ենք ուղարկել միայն տեքստ:")

    async def test_ask_gpt4o_start_command(self):
        message = MagicMock(spec=Message)
        message.text = "start"
        message.from_user.first_name = "TestUser"
        message.reply = AsyncMock()

        await ask_gpt4o(message)
        message.reply.assert_called_once_with("Բարև, TestUser! Ինչով կարող եմ օգնել?")

    async def test_ask_gpt4o_conversation(self):
        message = MagicMock(spec=Message)
        message.text = "Test query"
        message.from_user.id = 12345
        message.bot = AsyncMock()
        message.reply = AsyncMock()

        with patch('asyncio.create_task'):
            with patch('main.ask_gpt_async', return_value="Test response"):
                await ask_gpt4o(message)
                # Check that the response is added to user_caches
                self.assertIn(12345, user_caches)
                self.assertEqual(len(user_caches[12345]), 2)
                message.reply.assert_called_once_with(text="Test response")