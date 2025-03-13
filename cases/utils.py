from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import ResourceExistsError
from django.conf import settings

from decouple import config

import logging
logger = logging.getLogger(__name__)

def upload_to_azure_blob(file_obj, filename):
    use_azure_storage = config('USE_AZURE_STORAGE', default='False').lower() == 'true'
    print('user azure storage ? ', use_azure_storage)

    """
    Upload file to Azure Blob Storage
    Returns URL of uploaded blob
    """

    if not use_azure_storage:
        # RETURN FAKE URL FOR DEV TESTING
        print("DEBUG MODE: Skipping Azure Upload")
        return f"http://fake-azure-url.com/video.webm"

    try:

        print('use azure storage')
        logger.info('use azure storage')

        connection_string = settings.AZURE_STORAGE_CONNECTION_STRING
        container_name = settings.AZURE_STORAGE_CONTAINER

        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        container_client = blob_service_client.get_container_client(container_name)

        if not container_client.exists():
            print(f'creationg container: { container_name }')
            logger.info(f'creationg container: { container_name }')
        else:
            print(f'container { container_name } already exists')
            logger.info(f'container { container_name } already exists')

        # try:
        #     container_client = blob_service_client.create_container(container_name)
        # except ResourceExistsError:
        #     container_client = blob_service_client.get_container_client(container_name)

        blob_client = container_client.get_blob_client(filename)

        blob_client.upload_blob(file_obj, overwrite=True)
        print(f"Uplaoded { filename } to Azure Blob Storage")
        logger.info(f"Uplaoded { filename } to Azure Blob Storage")

        print(f'uploaded { filename } to blob storage: { blob_client.url }')
        logger.info(f'uploaded { filename } to blob storage: { blob_client.url }')

        # Return the blob URL
        return blob_client.url

    except Exception as e:
        print(f"Error uploading to Azure Blob Storage: { str(e) }")
        logger.info(f"Error uploading to Azure Blob Storage: { str(e) }")

        # raise
        return None
