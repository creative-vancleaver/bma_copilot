import os
import base64
import json
import pytz
import shutil
from pathlib import Path
from collections import defaultdict
from datetime import datetime
from decouple import config

from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views import View
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.storage import default_storage
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from .models import Case, Video
from .utils import upload_to_azure_blob
from .services.video_service import upload_video_notice, create_video_status, get_video_status, complete_video_status, get_cells_json

USE_AZURE_STORAGE = config('USE_AZURE_STORAGE', default='False').lower() == 'true'
USE_AZURE_SERVICES = config('USE_AZURE_SERVICES', default='False').lower() == 'true'

os.makedirs(os.path.join(settings.MEDIA_ROOT, "cases/screenshots"), exist_ok=True)

@login_required
def save_recording(request):

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
        crop_data = json.loads(request.POST.get('crop_data'))

        # FOR NOW EACH VIDEO WILL BE A NEW CASE
        # case = Case.objects.get(case_id=case_id)
        case = Case.objects.create(user=request.user)
        case_id = case.case_id
        video_id = f"{ case_id }_1"

        # GENERATE FILENAME + PATH
        # EACH CASE HAS 1 VIDEO - THEREFORE VIDEO_ID = 1.
        filename = f"{case_id}_1.webm"
        file_path = f"cases/{case_id}/recordings/{filename}"

        try:
            if USE_AZURE_STORAGE:
            # UPLOAD TO AZURE STORAGE BLOB
                blob_url = upload_to_azure_blob(video_file, filename)
                # blob_url = file_path

                payload = {
                    'video_id': video_id,
                    'TL_x': crop_data.get('TL_x'),
                    'TL_y': crop_data.get('TL_y'),
                    'BR_x': crop_data.get('BR_x'),
                    'BR_y': crop_data.get('BR_y')
                }

                response = upload_video_notice(payload)

                if response.get('statusCode') != 200:
                    return JsonResponse({
                        'success': False,
                        'error': f'video upload notice failed: { response.body.message }'
                    }, status=response.status)

            return JsonResponse({
                "success": True,
                "case": case.case_id,
                "video_id": video_id,
                "filename": filename,
            })
            
        except Exception as blob_error:
            # IF UPLOAD FAILS - DELETE VIDEO OBJECT
            # new_video.delete()
            raise blob_error
            
    except Exception as e:
        import traceback
        print(f"Error in save_recording: {str(e)}")
        print(traceback.format_exc())
        return JsonResponse({
            "success": False,
            "error": str(e)
        }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class VideoStatusView(View):

    def post(self, request):
        print(request)
        try:
            data = json.loads(request.body)
            print('data ', data)
            video_id = data.get('video_id')
            if not video_id:
                return JsonResponse({ 'error': 'Missing video_id' }, status=400)
            
            response = create_video_status(video_id)
            print('response = ', response)
            return JsonResponse(response)
        
        except json.JSONDecodeError:
            return JsonResponse({ 'error': 'Invalid JSON' }, status=400)
        
    def get(self, request, video_id=None):

        if not video_id:
            return JsonResponse({ 'error': 'Missing video_id' }, status=400)
        
        response = get_video_status(video_id)
        print(response)
        return JsonResponse(response)
    
    def put(self, request):
        try:
            data = json.loads(request.body)
            video_id = data.get('video_id')
            if not video_id:
                return JsonResponse({ 'error': 'Missing video_id' }, status=400)
            
            video_status_response = complete_video_status(video_id)

            # case_id = data.get('case_id')
            # cells_json_response = get_cells_json(case_id)

            # if cells_json_response.get('statusCode') != 200:
            #     return JsonResponse({
            #         'success': False,
            #         'error': 'Failed to fetch cell data'
            #     }, status=500)
            
            # try:
            
            #     cell_data = cells_json_response.get('body')
            #     print(cell_data)
            #     data_dir = Path('data/cells') 
            #     data_dir.mkdir(parents=True, exist_ok=True)

            #     with open(data_dir / f'{ case_id }.json', 'w') as f:
            #         json.dump(cell_data, f)

            # except Exception as e:
            #     print(str(e))

            return JsonResponse({
                'success': True,
                'message': 'Video status updated and cell data fetched'
            })

        except json.JSONDecodeError:
            return JsonResponse({ 'error': 'Invalid JSON' }, 400)

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

            if config('UPLOAD_TO_S3', default=True).lower() == 'true':
                result = save_to_s3_mount(case_id)
                if result['success']:
                    return JsonResponse({
                        'success': True,
                        'new_status': case.case_status
                    }, status=200)
                return JsonResponse(result, status=500)
        
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
        
    return JsonResponse({
        'success': False,
        'error': 'Invaid request method'
    }, status=500)

def save_to_s3_mount(case_id):
    local_cells_data = Path(f'/home/ubuntu/bma_copilot/data/cells/{ case_id }.json')
    s3_mount_path = Path(f'/home/ubuntu/S3/cells-json-updated{ case_id }.json')

    if not local_cells_data.exists():
        return ({
            'success': False,
            'error': 'Local cell data not found'
        })
    
    s3_mount_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        shutil.copy2(local_cells_data, s3_mount_path)
        return ({
            'success': True,
            'message': f'File {case_id}.json saved to S3'
        })
    
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

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
