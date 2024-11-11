# test_main.py

import unittest
from unittest.mock import AsyncMock, patch, MagicMock
from main import ask_gpt_async
import aiohttp
from main import start_command
from main import ask_gpt4o, user_caches


class TestMain(unittest.IsolatedAsyncioTestCase):

    async def test_ask_gpt_async_success(self):
        # Mock response returned by aiohttp client's session.post
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = {
            "choices": [{
                "message": {
                    "content": "Test response"
                }
            }]
        }

        # Mock the session.post() method
        mock_session = AsyncMock()
        mock_session.post.return_value.__aenter__.return_value = mock_response

        # Patch aiohttp.ClientSession to return the mocked session
        with patch('aiohttp.ClientSession', return_value=mock_session):
            result = await ask_gpt_async(model="gpt-4o", messages=[])
            self.assertEqual(result, "Test response")

    async def test_ask_gpt_async_error(self):
        # Mock response with an error status
        mock_response = AsyncMock()
        mock_response.status = 400
        mock_response.text.return_value = "Bad Request"

        # Mock the session.post() method
        mock_session = AsyncMock()
        mock_session.post.return_value.__aenter__.return_value = mock_response

        # Patch aiohttp.ClientSession
        with patch('aiohttp.ClientSession', return_value=mock_session):
            result = await ask_gpt_async(model="gpt-4o", messages=[])
            self.assertEqual(result, "Տեղի ունեցել սխալ․ 400")
            

    async def test_ask_gpt4o_no_text(self):
        message = MagicMock()
        message.text = None
        message.reply = AsyncMock()

        await ask_gpt4o(message)
        message.reply.assert_called_once_with(
            "Ես կարող եմ մշակել միայն տեքստային հաղորդագրությունները: Խնդրում ենք ուղարկել միայն տեքստ:"
        )


    async def test_ask_gpt4o_start_command(self):
        message = MagicMock()
        message.text = "start"
        message.from_user.first_name = "TestUser"
        message.reply = AsyncMock()

        await ask_gpt4o(message)
        message.reply.assert_called_once_with("Բարև, TestUser! Ինչով կարող եմ օգնել?")


    async def test_ask_gpt4o_conversation(self):
        message = MagicMock()
        message.text = "Test query"
        message.from_user.id = 12345
        message.chat.id = 67890
        message.bot = AsyncMock()
        message.bot.send_chat_action = AsyncMock()
        message.reply = AsyncMock()

        # Mock ask_gpt_async to return a predefined response
        with patch('main.ask_gpt_async', return_value="Test response"):
            await ask_gpt4o(message)

            # Verify that the user's conversation history is updated
            self.assertIn(12345, user_caches)
            self.assertEqual(len(user_caches[12345]), 2)
            message.reply.assert_called_once_with(text="Test response")


    async def test_start_command(self):
        message = MagicMock()
        message.from_user.first_name = "TestUser"
        message.reply = AsyncMock()

        await start_command(message)
        message.reply.assert_called_once_with("Բարև, TestUser! Ինչով կարող եմ օգնել?")