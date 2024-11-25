import unittest
from unittest.mock import patch, AsyncMock
from src.openai_requests import ask_gpt_async

class TestOpenAIRequests(unittest.IsolatedAsyncioTestCase):
    @patch('openai_requests.handle_errors')
    @patch('aiohttp.ClientSession.post')
    async def test_ask_gpt_async_success(self, mock_post, mock_handle_errors):
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = {"choices": [{"message": {"content": "Test response"}}]}
        mock_post.return_value.__aenter__.return_value = mock_response
        mock_handle_errors.return_value = None

        response = await ask_gpt_async(
            model="gpt-4o",
            messages=[{"role": "user", "content": "Hello"}]
        )
        self.assertEqual(response, "Test response")

    @patch('openai_requests.handle_errors')
    @patch('aiohttp.ClientSession.post')
    async def test_ask_gpt_async_error(self, mock_post, mock_handle_errors):
        mock_response = AsyncMock()
        mock_response.status = 500
        mock_response.text.return_value = "Internal Server Error"
        mock_post.return_value.__aenter__.return_value = mock_response
        mock_handle_errors.return_value = "An error occurred: 500"

        response = await ask_gpt_async(
            model="gpt-4o",
            messages=[{"role": "user", "content": "Hello"}]
        )
        self.assertEqual(response, "An error occurred: 500")

if __name__ == '__main__':
    unittest.main()
