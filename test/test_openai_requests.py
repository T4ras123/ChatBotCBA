import pytest
import asyncio
from unittest.mock import patch, AsyncMock
from openai_requests import ask_gpt_async
from handle_errors import handle_errors

@pytest.mark.asyncio
async def test_ask_gpt_async_success():
    with patch('aiohttp.ClientSession.post') as mock_post:
        mock_response = AsyncMock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Test response"}}]
        }
        mock_response.status = 200
        mock_post.return_value.__aenter__.return_value = mock_response
        
        response = await ask_gpt_async("gpt-4o", [{"role": "user", "content": "Hello"}])
        assert response == "Test response"

@pytest.mark.asyncio
async def test_ask_gpt_async_error():
    with patch('aiohttp.ClientSession.post') as mock_post, \
         patch('handle_errors.handle_errors') as mock_handle_errors:
        mock_handle_errors.return_value = "Error occurred"
        response = await ask_gpt_async("gpt-4o", [{"role": "user", "content": "Hello"}])
        assert response == "Error occurred"
