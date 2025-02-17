import requests
from decouple import config

API_HEADERS = {
    'Content-Type': 'application/josn',
    'x-api-key': config('VIDEO_API_KEY')
}

CREATE_VIDEO_STATUS_URL = "https://d9bf4394p9.execute-api.us-east-2.amazonaws.com/prod"
GET_VIDEO_STATUS_URL = "https://46alsc95ej.execute-api.us-east-2.amazonaws.com/prod"
COMPLETE_VIDEO_STATUS_URL = "https://cfsbmp46wb.execute-api.us-east-2.amazonaws.com/prod"

def create_video_status(video_id):
    payload = { "video_id": video_id }
    response = requests.post(CREATE_VIDEO_STATUS_URL, headers=API_HEADERS, json=payload)
    return response.json()

def get_video_status(video_id):
    payload = { 'video_id': video_id }
    response = requests.get(GET_VIDEO_STATUS_URL, headers=API_HEADERS, json=payload)
    return response.json()

def complete_video_status(video_id):
    payload = { 'video_id': video_id }
    response = requests.put(COMPLETE_VIDEO_STATUS_URL, headers=API_HEADERS, json=payload)
    return response.json()