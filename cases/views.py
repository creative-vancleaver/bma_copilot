import os
import base64
import pytz
import time

from datetime import datetime

from django.conf import settings
from django.http import JsonResponse
from django.core.files.storage import default_storage
from django.views.decorators.csrf import csrf_exempt

from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Case
from .serializers import CaseSerializer

class CaseViewSet(viewsets.ModelViewSet):
    
    queryset = Case.objects.all()
    serializer_class = CaseSerializer
    permission_classes = [IsAuthenticated]

os.makedirs(os.path.join(settings.MEDIA_ROOT, "cases/screenshots"), exist_ok=True)

@csrf_exempt # DEV ENV ONLY
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

        # pst = pytz.timezone('America/Los_Angeles')
        # current_time = datetime.now(pst)
        # timestamp = current_time.strftime("%Y%m%d-%H%M%S")
        # filename = f"recording_{ timestamp }.webm"
        # # filepath = os.path.join("cases/recodings", filename)
        # filepath = os.path.join("cases", str(case_id), "recordings", filename)

        # os.makedirs(os.path.join(settings.MEDIA_ROOT, "cases", str(case_id), "recordings"), exist_ok=True)


        # file_path_full = os.path.join(settings.MEDIA_ROOT, filepath)
        # with default_storage.open(file_path_full, 'wb') as f:
        #     for chunk in video_file.chunks():
        #         f.write(chunk)

        case = Case.objects.get(id=case_id)
        # case.video_file_path = filepath
        case.video_file.save(video_file.name, video_file)
        case.save()

        # file_url = os.path.join(settings.MEDIA_URL, filepath)
        # print("Saved video file at:", file_url)

        return JsonResponse({
            "success": True,
            # "filename": filename,
            # "url": file_url,
            "filename": case.video_file.name,
            "url": case.video_file.url
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
