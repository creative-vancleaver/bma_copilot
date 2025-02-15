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
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
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

        # FOR NOW EACH VIDEO WILL BE A NEW CASE
        # case = Case.objects.get(case_id=case_id)
        case = Case.objects.create(user=request.user)
        case_id = case.case_id
        

        
        # Generate filename and path
        # EACH CASE HAS 1 VIDEO - THEREFORE VIDEO_ID = 1.
        filename = f"{case_id}_1.webm"
        file_path = f"cases/{case_id}/recordings/{filename}"

        print(filename)

        try:
            # if USE_AZURE_STORAGE:
            print('upload to blob')
            # UPLOAD TO AZURE STORAGE BLOB
            blob_url = upload_to_azure_blob(video_file, filename)
            # new_video.azure_url = blob_url
            # new_video.video_file_path = file_path
                
            # else:
            #     # Save locally
            #     local_path = os.path.join(settings.MEDIA_ROOT, file_path)
            #     os.makedirs(os.path.dirname(local_path), exist_ok=True)
                
            #     with open(local_path, 'wb+') as destination:
            #         for chunk in video_file.chunks():
            #             destination.write(chunk)


            return JsonResponse({
                "success": True,
                "case": case.case_id,
                "filename": filename,
            })
            
        except Exception as storage_error:
            # If storage fails, delete the video object
            # new_video.delete()
            raise storage_error
            
    except Exception as e:
        import traceback
        print(f"Error in save_recording: {str(e)}")
        print(traceback.format_exc())
        return JsonResponse({
            "success": False,
            "error": str(e)
        }, status=500)

@login_required
def update_case_status(request, case_id):

    if request.method == 'POST':

        try:
            case = get_object_or_404(Case, case_id=case_id)
        
            new_status = request.POST.get('status')

            valid_statuses = ['pending', 'in_progress', 'completed', 'archived']
            if new_status not in valid_statuses:
                return JsonResponse({
                    "success": False,
                    "error": 'Invaild status'
                }, status=400)
            
            case.case_status = new_status
            case.save()

            return JsonResponse({
                'success': True,
                'new_status': case.case_status
            })
        
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
        
    return JsonResponse({
        'success': False,
        'error': 'Invaid request method'
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
