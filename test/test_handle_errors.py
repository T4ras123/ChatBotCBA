import unittest
from unittest.mock import AsyncMock, patch
from handle_errors import handle_errors

class TestHandleErrors(unittest.IsolatedAsyncioTestCase):
    @patch('handle_errors.logging')
    async def test_handle_errors_no_error(self, mock_logging):
        response = AsyncMock()
        response.status = 200

        result = await handle_errors(response)
        self.assertIsNone(result)
        mock_logging.error.assert_not_called()

    @patch('handle_errors.logging')
    async def test_handle_errors_with_error(self, mock_logging):
        response = AsyncMock()
        response.status = 404
        response.text.return_value = "Not Found"

        result = await handle_errors(response)
        self.assertEqual(result, "An error occurred: 404")
        mock_logging.error.assert_called_with("API Error 404: Not Found")

if __name__ == '__main__':
    unittest.main()
