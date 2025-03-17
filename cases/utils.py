import os
from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions, ContentSettings
from azure.core.exceptions import ResourceExistsError
from datetime import datetime, timezone, timedelta
from django.conf import settings

from decouple import config

import logging
logger = logging.getLogger(__name__)


AZURE_ACCOUNT_NAME = config('AZZURE_ACCOUNT_NAME', default=None)
AZURE_ACCOUNT_KEY = config('AZURE_ACCOUNT_KEY', default=None)
AZURE_CONTAINER_NAME = config('AZURE_STORAGE_CONTAINER', default=None)

def generate_sas_token():

    if not AZURE_ACCOUNT_NAME or not AZURE_ACCOUNT_KEY or not AZURE_CONTAINER_NAME:
        raise ValueError('Azure Blob Storage credentials are missing or not loaded properly')
    
    try:
        expiry = datetime.now(timezone.utc) + timedelta(days=30)

        sas_token = generate_sas_token(
            AZURE_ACCOUNT_NAME,
            AZURE_CONTAINER_NAME,
            account_key=AZURE_ACCOUNT_KEY,
            permission=BlobSasPermissions(read=True, write=True, create=True, delete=True, list=True),
            expiry=expiry
        )

        return sas_token

    except Exception as e:
        logger.warning(f'Error generating SAS token: {e}')


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
    
    # sas_token = generate_sas_token()
    # if not sas_token:
    #     logger.warning('Failed to generate SAS token.')
    #     return False

    try:

        print('use azure storage')
        logger.info('use azure storage')

        connection_string = settings.AZURE_STORAGE_CONNECTION_STRING
        container_name = settings.AZURE_STORAGE_CONTAINER

        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        container_client = blob_service_client.get_container_client(container_name)

        if not container_client.exists():
            print(f'creating container: { container_name }')
            logger.info(f'creationg container: { container_name }')
        else:
            print(f'container { container_name } already exists')
            logger.info(f'container { container_name } already exists')

        # try:
        #     container_client = blob_service_client.create_container(container_name)
        # except ResourceExistsError:
        #     container_client = blob_service_client.get_container_client(container_name)

        blob_client = container_client.get_blob_client(filename)

        file_obj.seek(0, os.SEEK_END)
        file_size = file_obj.tell()
        file_obj.seek(0)

        chunk_size = 4 * 1024 * 1024 # 4MB CHUNKS

        if file_size < chunk_size:
            # SIMPLE UPLOAD FOR SMALL FILES
            blob_client.upload_blob(
                file_obj, 
                overwrite=True,
                content_settings=ContentSettings(content_typ="video/webm")
            )
        else:
            # USE CHUNKED UPLOAD FOR LARGE FILES
            blob_client.upload_blob(
                file_obj,
                overwrite=True,
                max_concurrency=4,
                blob_type="BlockBlob",
            )

            # SET CONTENT TYPE AFTER UPLOAD FOR LARGE FILES
            blob_client.set_http_headers(content_settings=ContentSettings(content_type="video/webm"))

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
        return False
