import os
import base64
import pytz
import time

import random
import copy
from collections import defaultdict
from datetime import datetime
from decouple import config

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
from cells.services.azure_service import CaseAzureService

USE_AZURE_STORAGE = config('USE_AZURE_STORAGE', default='False').lower() == 'true'
USE_AZURE_SERVICES = config('USE_AZURE_SERVICES', default='False').lower() == 'true'

class CaseViewSet(viewsets.ModelViewSet):

    # TEMP DISABLE AUTH FOR THIS VIEW
    authentication_classes = []
    permission_classes = [AllowAny]
    # permission_classes = [IsAuthenticated]
    
    queryset = Case.objects.all().order_by('case_id')
    serializer_class = CaseSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        print("USE_AZURE_STORAGE:", config('USE_AZURE_STORAGE', default='Not Found'))
        print("AZURE_STORAGE_CONNECTION_STRING:", config('AZURE_STORAGE_CONNECTION_STRING', default='Not Found'))
        print("AZURE_STORAGE_CONTAINER:", config('AZURE_STORAGE_CONTAINER', default='Not Found'))
                
        # Only sync with Azure if enabled
        if USE_AZURE_SERVICES:
            azure_service = CaseAzureService()
            for case in queryset:
                azure_service.sync_case(str(case.id))
            
        return queryset

    def perform_create(self, serializer):
        case = serializer.save()
        
        # Only sync with Azure if enabled
        if USE_AZURE_SERVICES:
            azure_service = CaseAzureService()
            azure_service.azure_db.create_case(
                case_id=str(case.id),
                case_name=case.name,
                case_description=case.description,
                case_date=case.date.strftime('%Y-%m-%d'),
                case_time=case.time.strftime('%H:%M:%S'),
                user_id=str(case.user.id)
            )

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
        print('video_file ', video_file)
        case = Case.objects.get(case_id=case_id)
        
        # Generate a unique ID for the video
        # pst = pytz.timezone('America/Los_Angeles')
        # current_time = datetime.now(pst)
        # video_id = f"vid_{current_time.strftime('%Y%m%d_%H%M%S')}_{random.randint(1000, 9999)}"
        
        # Create video object with generated ID
        new_video = Video.objects.create(
            # video_id=video_id,
            case=case
        )
        # new_video.video_id = f"{case.user.user_id}_{case.case_id}_{}"

        
        # Generate filename and path
        filename = f"{case.user.user_id}_{case.case_id}_{new_video.video_id}.webm"
        file_path = f"cases/{case_id}/recordings/{filename}"

        print('request ', request, request.FILES)

        try:
            if USE_AZURE_STORAGE:
                print('upload to blob')
                # Upload to Azure Blob Storage
                blob_url = upload_to_azure_blob(video_file, filename)
                new_video.azure_url = blob_url
                new_video.video_file_path = file_path
                print('blob url ', blob_url)
                
                # Sync with Azure DB
                # azure_service = CaseAzureService()
                # azure_service.azure_db.add_video(
                #     video_id=video_id,
                #     video_file_path=file_path,
                #     case_id=str(case_id)
                # )
            else:
                # Save locally
                local_path = os.path.join(settings.MEDIA_ROOT, file_path)
                os.makedirs(os.path.dirname(local_path), exist_ok=True)
                
                with open(local_path, 'wb+') as destination:
                    for chunk in video_file.chunks():
                        destination.write(chunk)
                
                new_video.video_file_path = file_path

            # Update video object
            # new_video.video_file.name = file_path
            # new_video.save()

            return JsonResponse({
                "success": True,
                "case": case.case_id,
                "video_id": new_video.video_id,
                "filename": filename,
                "video_file_path": new_video.video_file_path,
                "url": new_video.azure_url if USE_AZURE_STORAGE else new_video.video_file_path
            })
            
        except Exception as storage_error:
            # If storage fails, delete the video object
            new_video.delete()
            raise storage_error
            
    except Case.DoesNotExist:
        return JsonResponse({
            "success": False,
            "error": f"Case with ID {case_id} not found"
        }, status=404)
    except Exception as e:
        import traceback
        print(f"Error in save_recording: {str(e)}")
        print(traceback.format_exc())
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
