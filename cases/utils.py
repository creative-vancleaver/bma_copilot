from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import ResourceExistsError
from django.conf import settings

def upload_to_azure_blob(file_obj, filename):

    """
    Upload file to Azure Blob Storage
    Returns URL of uploaded blob
    """

    if settings.DEBUG and getattr(settings, 'SKIP_AZURE_UPLOAD', False):
        # RETURN FAKE URL FOR DEV TESTING
        return f"https://fake-azure-url.com/{filename}"

    try:

        connection_string = settings.AZURE_STORAGE_CONNECTION_STRING
        container_name = settings.AZURE_STORAGE_CONTAINER

        blob_service_client = BlobServiceClient.from_connection_string(connection_string)

        try:
            container_client = blob_service_client.create_container(container_name)
        except ResourceExistsError:
            container_client = blob_service_client.get_container_client(container_name)

        blob_client = container_client.get_blob_client(filename)

        blob_client.upload_blob(file_obj, overwrite=True)

        # Return the blob URL
        return blob_client.url

    except Exception as e:
        print(f"Error uploading to Azure Blob Storage: { str(e) }")
        raise
