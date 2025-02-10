from io import BytesIO
import azure.storage.blob

connection_string = "BlobEndpoint=https://videouploadsdeepheme.blob.core.windows.net/;QueueEndpoint=https://videouploadsdeepheme.queue.core.windows.net/;FileEndpoint=https://videouploadsdeepheme.file.core.windows.net/;TableEndpoint=https://videouploadsdeepheme.table.core.windows.net/;SharedAccessSignature=sv=2022-11-02&ss=b&srt=co&sp=rwiytfx&se=2025-03-01T04:29:05Z&st=2025-02-04T20:29:05Z&spr=https&sig=moJYh4m4mE8lipWGPa6uEevGP%2Brte17jK%2FySuLySDjI%3D"
blob_service_client = azure.storage.blob.BlobServiceClient.from_connection_string(connection_string)
region_container_name = "regions"
cell_container_name = "cells"
checkpoint_container_name = "checkpoints"
video_container_name = "videos"
regions_image_container_name = "regions"
cells_image_container_name = "cells"
region_container_client = blob_service_client.get_container_client(region_container_name)
cell_container_client = blob_service_client.get_container_client(cell_container_name)  
checkpoint_container_client = blob_service_client.get_container_client(checkpoint_container_name)
video_container_client = blob_service_client.get_container_client(video_container_name)
regions_image_container_client = blob_service_client.get_container_client(regions_image_container_name)
cells_image_container_client = blob_service_client.get_container_client(cells_image_container_name)

def get_object_buffer_path_from_blob(container_client, object_name):
    blob_client = container_client.get_blob_client(object_name)
    bytes_data = blob_client.download_blob().readall()
    return BytesIO(bytes_data)

if __name__ == "__main__":
    # ADD THESE TO ENVIRONMENT VARIABLES
    user_id = "1"
    case_id = "1_1"
    video_name = "1_1_42.webm"
    region_clf_ckpt_name = "region_clf_BMACopilotV1.ckpt"
    cell_detection_ckpt_name = "cell_detection_BMACopilotV1.pt"
    cell_clf_ckpt_name = "cell_clf_BMACopilotV1.ckpt"
    region_image_name = "1_1_42_187.jpg"
    cell_image_name = "1_1_42_187_9.jpg"
    print("Getting region clf ckpt")
    region_clf_ckpt_path = get_object_buffer_path_from_blob(checkpoint_container_client, region_clf_ckpt_name)
    print("Getting cell detection ckpt")
    cell_detection_ckpt_path = get_object_buffer_path_from_blob(checkpoint_container_client, cell_detection_ckpt_name)
    print("Getting cell clf ckpt")
    cell_clf_ckpt_path = get_object_buffer_path_from_blob(checkpoint_container_client, cell_clf_ckpt_name)
    print("Getting video")
    video_path = get_object_buffer_path_from_blob(video_container_client, video_name)
    print("Getting region image")
    region_image_path = get_object_buffer_path_from_blob(regions_image_container_client, region_image_name)
    print("Getting cell image")
    cell_image_path = get_object_buffer_path_from_blob(cells_image_container_client, cell_image_name)
