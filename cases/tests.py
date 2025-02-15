from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile

from unittest.mock import patch, MagicMock

from .utils import upload_to_azure_blob

class AzureUploadTest(TestCase):
    @patch('cases.utils.BlobServiceClient')
    def test_upload_to_azure_blob_test(self, mock_blob_service):

        # SETUP MOCK
        mock_blob_client = MagicMock()
        mock_blob_client.url = "https://fake-azure-url.com/video.webm"

        mock_container_client = MagicMock()
        mock_container_client.get_blob_client.return_value = mock_blob_client

        mock_blob_service.from_connection_string.return_value.get_container_client.return_value = mock_container_client

        # CREATE DUMMY FILE
        dummy_file = SimpleUploadedFile(
            "test_video.webm",
            b"file_content",
            content_type="video/webm"
        )

        # TEST UPLOAD FUNCTION
        result = upload_to_azure_blob(dummy_file, 'test_video.webm')

        # VERIFY RESULT
        self.assertEqual(result, 'http://fake-azure-url.com/video.webm')


