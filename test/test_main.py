# test_main.py

import unittest
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from unittest.mock import AsyncMock, patch, MagicMock
from main import ask_gpt_async, ask_gpt4o, start_command, user_caches
from aiogram.types import Message

class TestMain(unittest.IsolatedAsyncioTestCase):
    async def test_ask_gpt_async_success(self):
        # Mock response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={
            "choices": [{
                "message": {
                    "content": "Test response"
                }
            }]
        })

        # Mock session.post()
        mock_post_cm = AsyncMock()
        mock_post_cm.__aenter__.return_value = mock_response

        # Mock aiohttp.ClientSession()
        mock_session_cm = AsyncMock()
        mock_session_cm.__aenter__.return_value = AsyncMock(post=AsyncMock(return_value=mock_post_cm))

        with patch('aiohttp.ClientSession', return_value=mock_session_cm):
            result = await ask_gpt_async(model="gpt-4", messages=[])
            self.assertEqual(result, "Test response")

    async def test_ask_gpt_async_error(self):
        # Mock response
        mock_response = AsyncMock()
        mock_response.status = 400
        mock_response.text = AsyncMock(return_value="Bad Request")

        # Mock session.post()
        mock_post_cm = AsyncMock()
        mock_post_cm.__aenter__.return_value = mock_response

        # Mock aiohttp.ClientSession()
        mock_session_cm = AsyncMock()
        mock_session_cm.__aenter__.return_value = AsyncMock(post=AsyncMock(return_value=mock_post_cm))

        with patch('aiohttp.ClientSession', return_value=mock_session_cm):
            result = await ask_gpt_async(model="gpt-4", messages=[])
            self.assertEqual(result, "Տեղի ունեցել սխալ․ 400")

    async def test_start_command(self):
        message = MagicMock(spec=Message)
        message.from_user = MagicMock()
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
        message.from_user = MagicMock()
        message.from_user.first_name = "TestUser"
        message.reply = AsyncMock()

        await ask_gpt4o(message)
        message.reply.assert_called_once_with("Բարև, TestUser! Ինչով կարող եմ օգնել?")

    async def test_ask_gpt4o_conversation(self):
        message = MagicMock(spec=Message)
        message.text = "Test query"
        message.from_user = MagicMock()
        message.from_user.id = 12345
        message.bot = AsyncMock()
        message.reply = AsyncMock()

        with patch('asyncio.create_task', return_value=AsyncMock()):
            with patch('main.ask_gpt_async', return_value="Test response"):
                await ask_gpt4o(message)
                # Check that the response is added to user_caches
                self.assertIn(12345, user_caches)
                self.assertEqual(len(user_caches[12345]), 2)
                message.reply.assert_called_once_with(text="Test response")

if __name__ == '__main__':
    unittest.main()