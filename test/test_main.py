# test_main.py

import unittest
from unittest.mock import AsyncMock, patch, MagicMock
from main import ask_gpt_async, start_command, ask_gpt4o, user_caches
from aiogram.types import Message

class TestMain(unittest.IsolatedAsyncioTestCase):

    async def test_ask_gpt_async_success(self):
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={
            "choices": [{
                "message": {
                    "content": "Test response"
                }
            }]
        })

        mock_post = AsyncMock()
        mock_post.__aenter__.return_value = mock_response

        mock_session = AsyncMock()
        mock_session.post.return_value = mock_post

        mock_client_session = AsyncMock()
        mock_client_session.__aenter__.return_value = mock_session

        with patch('aiohttp.ClientSession', return_value=mock_client_session):
            result = await ask_gpt_async(model="gpt-4o", messages=[])
            self.assertEqual(result, "Test response")

    async def test_ask_gpt_async_error(self):
        mock_response = AsyncMock()
        mock_response.status = 400
        mock_response.text = AsyncMock(return_value="Bad Request")

        mock_post = AsyncMock()
        mock_post.__aenter__.return_value = mock_response

        mock_session = AsyncMock()
        mock_session.post.return_value = mock_post

        mock_client_session = AsyncMock()
        mock_client_session.__aenter__.return_value = mock_session

        with patch('aiohttp.ClientSession', return_value=mock_client_session):
            result = await ask_gpt_async(model="gpt-4o", messages=[])
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
        message.chat = MagicMock()
        message.chat.id = 67890
        message.bot = AsyncMock()
        message.bot.send_chat_action = AsyncMock()
        message.reply = AsyncMock()

        with patch('main.ask_gpt_async', return_value="Test response"):
            await ask_gpt4o(message)
            self.assertIn(12345, user_caches)
            self.assertEqual(len(user_caches[12345]), 2)
            message.reply.assert_called_once_with(text="Test response")

if __name__ == '__main__':
    unittest.main()