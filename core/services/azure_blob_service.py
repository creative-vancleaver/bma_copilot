from io import BytesIO
from azure.storage.blob import BlobServiceClient
from decouple import config

# LOAD CONNECTION STRING FROM ENV
connection_string = config('AZURE_STORAGE_CONNECTION_STRING')
blob_service_client = BlobServiceClient.from_connection_string(connection_string)

# DEFINE CONTAINERS
CONTAINERS = {
    "regions": blob_service_client.get_container_client("regions"),
    "cells": blob_service_client.get_container_client("cells"),
    "videos": blob_service_client.get_container_client("videos")
}

def get_blob_url(container_name, blob_name):
    # GENERATE DIRECT URL FOR AN AZURE BLOB

    container_client = CONTAINERS.get(container_name)
    if not container_client:
        raise ValueError(f"Invalid container name: { container_name }")
    
    blob_client = container_client.get_blob_client(blob_name)
    return blob_client.url