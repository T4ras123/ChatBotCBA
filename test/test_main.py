# test_main.py

import unittest
from unittest.mock import AsyncMock, patch, MagicMock
from main import ask_gpt_async, start_command, ask_gpt4o, user_caches
from aiogram.types import Message

class TestMain(unittest.IsolatedAsyncioTestCase):

    async def test_ask_gpt_async_success(self):
        # Mock response returned by session.post
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={
            "choices": [{
                "message": {
                    "content": "Test response"
                }
            }]
        })

        # Mock session.post to return an async context manager
        mock_session_post = AsyncMock()
        mock_session_post.__aenter__.return_value = mock_response

        # Mock session to have a post method that returns the mock_session_post
        mock_session = AsyncMock()
        mock_session.post.return_value = mock_session_post

        # Mock aiohttp.ClientSession to return a context manager returning mock_session
        mock_client_session = AsyncMock()
        mock_client_session.__aenter__.return_value = mock_session

        with patch('aiohttp.ClientSession', return_value=mock_client_session):
            result = await ask_gpt_async(model="gpt-4o", messages=[])
            self.assertEqual(result, "Test response")

    async def test_ask_gpt_async_error(self):
        # Mock response with an error status
        mock_response = AsyncMock()
        mock_response.status = 400
        mock_response.text = AsyncMock(return_value="Bad Request")

        # Mock session.post to return an async context manager
        mock_session_post = AsyncMock()
        mock_session_post.__aenter__.return_value = mock_response

        # Mock session to have a post method that returns the mock_session_post
        mock_session = AsyncMock()
        mock_session.post.return_value = mock_session_post

        # Mock aiohttp.ClientSession to return a context manager returning mock_session
        mock_client_session = AsyncMock()
        mock_client_session.__aenter__.return_value = mock_session

        with patch('aiohttp.ClientSession', return_value=mock_client_session):
            result = await ask_gpt_async(model="gpt-4o", messages=[])
            self.assertEqual(result, "Տեղի ունեցել սխալ․ 400")

    async def test_start_command(self):
        message = MagicMock()
        message.from_user.first_name = "TestUser"
        message.reply = AsyncMock()

        await start_command(message)
        message.reply.assert_called_once_with("Բարև, TestUser! Ինչով կարող եմ օգնել?")


if __name__ == '__main__':
    unittest.main()