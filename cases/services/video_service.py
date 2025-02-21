import json
import requests
from decouple import config

API_HEADERS = {
    'Content-Type': 'application/json',
    'x-api-key': config('VIDEO_API_KEY')
}

VIDEO_UPLOAD_NOTIFICATION = "https://b8hyouows0.execute-api.us-east-2.amazonaws.com/prod"
CREATE_VIDEO_STATUS_URL = "https://d9bf4394p9.execute-api.us-east-2.amazonaws.com/prod"
GET_VIDEO_STATUS_URL = "https://46alsc95ej.execute-api.us-east-2.amazonaws.com/prod"
COMPLETE_VIDEO_STATUS_URL = "https://cfsbmp46wb.execute-api.us-east-2.amazonaws.com/prod"
CELLS_JSON_FILE = "https://jh8mumwvve.execute-api.us-east-2.amazonaws.com/prod"
# 'https://jh8mumwvve.execute-api.us-east-2.amazonaws.com/prod'

def upload_video_notice(payload):
    print('upload_video_notice ', payload)
       # ✅ Validate JSON structure before sending request
    try:
        json_payload = json.dumps(payload)  # Ensure serialization works
        print("Final JSON Payload:", json_payload)  # Debugging
    except TypeError as e:
        print("❌ JSON Serialization Error:", e)
        return {"error": "Invalid JSON payload"}
    response = requests.put(VIDEO_UPLOAD_NOTIFICATION, headers=API_HEADERS, json=payload)
    return response.json()

def create_video_status(video_id):
    payload = { "video_id": video_id }
       # ✅ Validate JSON structure before sending request
    try:
        json_payload = json.dumps(payload)  # Ensure serialization works
        print("Final JSON Payload:", json_payload)  # Debugging
    except TypeError as e:
        print("❌ JSON Serialization Error:", e)
        return {"error": "Invalid JSON payload"}
    response = requests.post(CREATE_VIDEO_STATUS_URL, headers=API_HEADERS, json=payload)
    return response.json()

def get_video_status(video_id):
    payload = { 'video_id': video_id }
    response = requests.get(GET_VIDEO_STATUS_URL, headers=API_HEADERS, json=payload)
    print('get_video_status ', response)
    print('get_video_status ', response.json())
    return response.json()

def complete_video_status(video_id):
    payload = { 'video_id': video_id }
    response = requests.put(COMPLETE_VIDEO_STATUS_URL, headers=API_HEADERS, json=payload)
    return response.json()

def get_cells_json(case_id):
    payload = { 'case_id': case_id }
    response = requests.get(CELLS_JSON_FILE, headers=API_HEADERS, json=payload)
    print('get_cells_json response ', response)
    return response.json()