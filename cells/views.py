import json
import pandas as pd
from decouple import config

from django.db.models import Count, F, Value, Case, When, IntegerField, Subquery, OuterRef
from django.db.models.functions import Coalesce
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

from core.services.azure_blob_service import get_blob_url
from .models import Cell, CellDetection, CellClassification


CELL_ORDER = [
    'blasts_and_blast_equivalents', 'promyelocytes', 'myelocytes', 'metamyelocytes', 'neutrophils', 'monocytes', 'eosinophils', 'lymphocytes', 'plasma_cells', 'erythroid_precursors', 'skippocytes',
]

USE_AZURE_SERVICES = config('USE_AZURE_SERVICES', default='False') == 'True'

class CellView(View):

    def get_cell_counts(self, case_id):
        queryset = (
            Cell.objects
            .filter(region__video_id__case__case_id=case_id)
            .annotate(
                ai_class=Subquery(
                    CellClassification.objects.filter(cell=OuterRef("cell_id")).values("ai_cell_class")[:1]
                ),
                user_class=Subquery(
                    CellClassification.objects.filter(cell=OuterRef("cell_id")).values("user_cell_class")[:1]
                ),
                class_name=Subquery(
                    CellClassification.objects
                    .filter(cell=OuterRef('cell_id'))
                    .values("user_cell_class")[:1] # PRIORITIZE USER CLASSIFICATION
                )
            )
            .values("class_name", "cell_id")
            .annotate(cell_count=Count("cell_id"))
            .order_by('class_name')
        )    

        cell_counts_dict = {}
        for item in queryset:
            class_name = item["class_name"]
            cell_counts_dict[class_name] = cell_counts_dict.get(class_name, 0) + item["cell_count"]

        cell_counts = [
            {"class_name": class_name, "cell_count": cell_counts_dict.get(class_name, 0)}
            for class_name in CELL_ORDER
        ]

        return cell_counts

    def get_diff_counts(self, case_id):
        cell_counts = self.get_cell_counts(case_id)
        filtered_counts = [item for item in cell_counts if item["class_name"] != "skippocytes"]

        total_cells = sum(item['cell_count'] for item in filtered_counts)

        if total_cells == 0:
            return {
                'percentages': { class_name: 0.0 for class_name in CELL_ORDER if class_name != 'skippocytes' },
                'counts': {item['class_name']: item['cell_count'] for item in cell_counts }
            }
        
        diff = {
            'percentages': {
                item['class_name']: round((item['cell_count'] / total_cells) * 100, 1)
                for item in filtered_counts
            },
            'counts': {
                item['class_name']: item['cell_count'] for item in cell_counts
            }
        }
        
        return diff
    
    def get(self, request, case_id, *args, **kwargs):
        response_data = {}

        if request.query_params.get("type") == 'differential':
            response_data['diff_counts'] = self.get_diff_counts(case_id)
        elif request.query_params.get("type") == 'cell_counts':
            response_data['cell_counts'] = self.get_cell_counts(case_id)
        else:
            response_data['diff_counts'] = self.get_diff_counts(case_id)
            response_data['cell_counts'] = self.get_cell_counts(case_id)

        return JsonResponse(response_data, status=200)
    
    @method_decorator(login_required)
    def post(self, request, case_id, *args, **kwargs):
        try:
            try:
                data = json.loads(request.body)
            except json.JSONDecodeError:
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid format'
                }, status=400)
            
            cell_id = data.get('cell_id')
            new_label = data.get('cell_label')

            if not cell_id or not new_label:
                return JsonResponse({ 
                    'success': False, 
                    'error': 'missing required fields'
                    }, status=400)
                     
            cell = get_object_or_404(Cell, cell_id=cell_id)

            cell_class, created = CellClassification.objects.get_or_create(
                cell=cell,
                defaults={"user_cell_class": new_label}
            )

            if not created:
                cell_class.user_cell_class = new_label
                cell_class.save()

            updated_cell_counts = self.get_cell_counts(case_id)
            updated_diff_counts = self.get_diff_counts(case_id)

            return JsonResponse({
                "success": True,
                "cell_counts": updated_cell_counts,
                "diff_counts": updated_diff_counts
            }, status=200)

        except Exception as e:
            return JsonResponse({
                "success": False,
                "error": str(e)
            }, status=500)

def get_blob_direct_url(request, container_name, blob_name):

    # RETURN DIRECT URL OF AZURE BLOB INSTEAD OF DOWNLOADING IT
    try:
        url = get_blob_url(container_name, blob_name)
        return JsonResponse({ "url": url })
    except Exception as e:
        return JsonResponse({ "error": str(e)}, status=500)
