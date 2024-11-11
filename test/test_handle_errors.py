import unittest
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from unittest.mock import AsyncMock
from handle_errors import handle_errors

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
        self.assertEqual(result, "Տեղի ունեցավ սխալ․ 404")  # Updated expected string

    async def test_handle_errors_server_error(self):
        response = AsyncMock()
        response.status = 500
        response.text = AsyncMock(return_value="Internal Server Error")
        result = await handle_errors(response)
        self.assertEqual(result, "Տեղի ունեցավ սխալ․ 500")  # Updated expected string

    async def test_handle_errors_boundary_low(self):
        response = AsyncMock()
        response.status = 199
        response.text = AsyncMock(return_value="Previous")
        result = await handle_errors(response)
        self.assertEqual(result, "Տեղի ունեցավ սխալ․ 199")

    async def test_handle_errors_boundary_high(self):
        response = AsyncMock()
        response.status = 300
        response.text = AsyncMock(return_value="Multiple Choices")
        result = await handle_errors(response)
        self.assertEqual(result, "Տեղի ունեցավ սխալ․ 300")

if __name__ == '__main__':
    unittest.main()