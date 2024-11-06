import unittest
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from unittest.mock import AsyncMock
from handle_errors import handle_errors

# ... rest of your test code ...
class TestHandleErrors(unittest.IsolatedAsyncioTestCase):
    async def test_handle_errors_success(self):
        response = AsyncMock()
        response.status = 200
        result = await handle_errors(response)
        self.assertIsNone(result)

    async def test_handle_errors_client_error(self):
        response = AsyncMock()
        response.status = 404
        response.text = AsyncMock(return_value="Not Found")
        result = await handle_errors(response)
        self.assertEqual(result, "Տեղի ունեցել սխալ․ 404")

    async def test_handle_errors_server_error(self):
        response = AsyncMock()
        response.status = 500
        response.text = AsyncMock(return_value="Internal Server Error")
        result = await handle_errors(response)
        self.assertEqual(result, "Տեղի ունեցել սխալ․ 500")