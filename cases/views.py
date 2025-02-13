import os
import base64
import pytz
import time

import random
import copy
from collections import defaultdict

from datetime import datetime

from django.conf import settings
from django.http import JsonResponse
from django.core.files.storage import default_storage
from django.views.decorators.csrf import csrf_exempt

from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import Case, Video
from .serializers import CaseSerializer
from .utils import upload_to_azure_blob

class CaseViewSet(viewsets.ModelViewSet):
    
    # TEMP DISABLE AUTH FOR THIS VIEW
    authentication_classes = []
    permission_classes = [AllowAny]
    # permission_classes = [IsAuthenticated]
    
    queryset = Case.objects.all().order_by('id')
    serializer_class = CaseSerializer


os.makedirs(os.path.join(settings.MEDIA_ROOT, "cases/screenshots"), exist_ok=True)

@csrf_exempt # EXEMPT IN DEV ONLY
def save_recording(request, case_id):

    if request.method != 'POST':
        return JsonResponse({
            "success": False,
            "error": "Invalid request method."
        }, status=400)
    
    try:

        if "video" not in request.FILES:
            return JsonResponse({
                "success": False,
                "error": "No video file received."
            }, status=400)
        
        video_file = request.FILES["video"]

        case = Case.objects.get(id=case_id)
        new_video = Video.objects.create(case=case)
        
        # INITIALIZE NEW VIDEO OBJECT
        # UNIQUE FILENAME
        pst = pytz.timezone('America/Los_Angeles')
        current_time = datetime.now(pst)
        timestamp = current_time.strftime("%Y%m%d-%H%M%S")
        # filename = f"recording_{ timestamp }.webm"
        user_id = case.user.id
        video_id = new_video.id
        filename = f"{user_id}_{case.id}_{video_id}.webm"

        # UPLOAD TO AZURE BLOB STORAGE
        blob_url = upload_to_azure_blob(video_file, f"cases/{case_id}/recordings/{filename}")

        # SAVE FILE TO VIDEO OBJECT
        # new_video = Video(case=case)
        new_video.video_file.name = f"cases/{case_id}/recordings/{filename}"
        new_video.azure_url = blob_url
        new_video.save()

        print('new video: ', new_video.video_file, new_video.azure_url)

        return JsonResponse({
            "success": True,
            "case": case.id,
            "filename": new_video.video_file.name,
            "url": new_video.video_file.url
        })
    
    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": str(e)
        }, status=500)

@csrf_exempt
def save_screenshot(request, case_id):

    if request.method != 'POST':
        return JsonResponse({
            "success": False,
            "error": "Invalid request method."
        }, status=400)
    
    try:

        data = request.POST.get("image")
        if not data:
            return JsonResponse({
                "success": False,
                "error": "No image data received"
            }, status=400)
        
        image_data = base64.b64decode(data.split(",")[1])

        pst = pytz.timezone('America/Los_Angeles')
        current_time = datetime.now(pst)
        timestamp = current_time.strftime("%Y%m%d-%H%M%S")
        filename = f"screenshot_{ timestamp }.jpg"
        filepath = os.path.join(settings.MEDIA_ROOT, "cases/screenshots", filename)

        with open(filepath, "wb") as f:
            f.write(image_data)

        case = Case.objects.get(id=case_id)
        case.video_file_path = f"cases/screenshots/{ filename }"
        case.save()

        file_url = os.path.join(settings.MEDIA_URL, "cases/screenshots", filename)
        print('file_url ', file_url)

        return JsonResponse({
            "success": True,
            "filename": filename,
            "url": file_url
        })
    
    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": str(e)
        }, status=500)
