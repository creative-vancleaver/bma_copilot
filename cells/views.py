from django.db.models import Count, F, Value, Case, When, IntegerField, Subquery, OuterRef
from django.db.models.functions import Coalesce
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from .models import Cell, CellDetection, CellClassification
from .serializers import CellSerializer, CellDetectionSerializer, CellClassificationSerializer

from rest_framework import status, viewsets
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from rest_framework.decorators import action

CELL_ORDER = [
    'blast', 'promyelocyte', 'myelocyte', 'metamyelocyte', 'neutrophil', 'monocyte', 'eosinophil', 
    'basophil', 'lymphocyte', 'plasma-cell', 'erythroid-precursor', 'skippocyte', 'unclassified'
]

class CellViewSet(viewsets.ModelViewSet):

    authentication_classes = []
    permission_classes = [AllowAny]

    queryset = Cell.objects.all().order_by('-id')
    serializer_class = CellSerializer

    def get_queryset(self):
        return Cell.objects.select_related(
            'region',
            'region__case',
            'detection',
            'classification'
        ).all().order_by('-id')
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    # GET DETECTION DETAILS @ cell/<cell_id>/detection_details
    @action(detail=True, methods=['get'])
    def detection_details(self, request, pk=None):
        cell = self.get_object()
        if not hasattr(cell, 'detection') or cell.detection is None:
            return Response({
                "success": False,
                "message": "No detection data available for this cell."
            }, status=status.HTTP_404_NOT_FOUND)
        serializer = CellDetectionSerializer(cell.detection)
        return Response(serializer.data)

    # GET CLASSIFICATION DETAILS @ cell/<cell_id>/classification_details
    @action(detail=True, methods=['get'])
    def classification_details(self, request, pk=None):
        cell = self.get_object()
        if not hasattr(cell, 'classification') or cell.classification is None:
            return Response({
                "success": False,
                "message": "No classification data available for this cell."
            }, status=status.HTTP_404_NOT_FOUND)
        serializer = CellClassificationSerializer(cell.classification)
        return Response(serializer.data)

class LabelCellView(APIView):
    authentication_classes = [JWTAuthentication]  # Ensure only JWT auth is used
    permission_classes = [IsAuthenticated]  # Require login

    def post(self, request, *args, **kwargs):
        try:

            cell_id = request.data.get('cell_id')
            user_label = request.data.get('cell_label')

            if not cell_id or not user_label:
                return Response({
                    'success': False,
                    'error': 'Missing cell or label.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # cell_class = get_object_or_404(CellClassification, cell__id=cell_id)
            cell = get_object_or_404(Cell, id=cell_id)

            cell_class, created = CellClassification.objects.get_or_create(
                cell=cell,
                defaults={"user_class": user_label}
            )

            if not created:
                cell_class.user_class = user_label
                cell_class.save()

            return Response({
                "success": True,
                "new_cell_class": cell_class.user_class
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "success": False,
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CellStatsView(APIView):

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_cell_counts(self, case_id):

        queryset = (
            Cell.objects
            .filter(region__case_id=case_id)
            .annotate(
                ai_class=Subquery(
                    CellClassification.objects.filter(cell=OuterRef("id")).values("ai_class")[:1]
                ),
                user_class=Subquery(
                    CellClassification.objects.filter(cell=OuterRef("id")).values("user_class")[:1]
                ),
                class_name=Coalesce(
                    Subquery(CellClassification.objects.filter(cell=OuterRef("id")).values("user_class")[:1]),
                    Subquery(CellClassification.objects.filter(cell=OuterRef("id")).values("ai_class")[:1]),
                    Value("unclassified")
                )
            )
            .values("class_name")
            .annotate(cell_count=Count("id"))
        )

        cell_counts_dict = {
            item["class_name"]: item["cell_count"] for item in queryset
        }

        cell_counts = [
            {"class_name": class_name, "cell_count": cell_counts_dict.get(class_name, 0)}
            for class_name in CELL_ORDER
        ]

        return cell_counts
    
    def get_diff_counts(self, case_id):

        cell_counts = self.get_cell_counts(case_id)
        total_cells = sum(item['cell_count'] for item in cell_counts)

        if total_cells == 0:
            return {class_name: 0.0 for class_name in CELL_ORDER}
        
        return {
            item['class_name']: round((item['cell_count'] / total_cells) * 100, 1)
            for item in cell_counts
        }
    
    def get(self, request, case_id, *args, **kwargs):

        response_data = {}

        if request.query_params.get("type") == 'differential':
            response_data['diff_counts'] = self.get_diff_counts(case_id)
        elif request.query_params.get("type") == 'cell_counts':
            response_data['cell_counts'] = self.get_cell_counts(case_id)
        else:
            response_data['diff_counts'] = self.get_diff_counts(case_id)
            response_data['cell_counts'] = self.get_cell_counts(case_id)

        return Response(response_data, status=status.HTTP_200_OK)
    
    def post(self, request, case_id, *args, **kwargs):

        try:
            cell_id = request.data.get('cell_id')
            new_label =request.data.get('cell_label')

            if not cell_id or not new_label:
                return Response({ 'success': False, 'error': 'missing required fields'}, status=status.HTTP_400_BAD_REQUEST)
                     
            # cell_class = get_object_or_404(CellClassification, cell__id=cell_id)
            cell = get_object_or_404(Cell, id=cell_id)

            cell_class, created = CellClassification.objects.get_or_create(
                cell=cell,
                defaults={"user_class": new_label}
            )

            if not created:
                cell_class.user_class = new_label
                cell_class.save()

            updated_cell_counts = self.get_cell_counts(case_id)
            updated_diff_counts = self.get_diff_counts(case_id)

            return Response({
                "success": True,
                "cell_counts": updated_cell_counts,
                "diff_counts": updated_diff_counts
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "success": False,
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class CellClassCountView(APIView):

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_cell_counts(self, case_id):

        queryset = (
            CellClassification.objects
            .filter(cell__region__case_id=case_id)
            .annotate(class_name=Coalesce(F("user_class"), F("ai_class")))  # Use user_class if available
            .values("class_name")
            .annotate(cell_count=Count("cell_id"))
        )

        # Convert queryset to list and apply custom sorting
        cell_counts = list(queryset)

        # Sort the results based on CELL_ORDER, placing unrecognized classes at the end
        cell_counts.sort(key=lambda x: CELL_ORDER.index(x["class_name"]) if x["class_name"] in CELL_ORDER else len(CELL_ORDER))

        return cell_counts

    def get(self, request, case_id, *args, **kwargs):

        cell_counts = self.get_cell_counts(case_id)

        return Response({
            "cell_counts": cell_counts,
        })
    
class DifferentialCountView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_diff(self, case_id):

        cell_count_view = CellClassCountView()
        cell_counts = list(cell_count_view.get_cell_counts(case_id))

        total_cells = sum(item['cell_count'] for item in cell_counts)

        if total_cells == 0:
            return Response({ "diff_counts": {} })
        
        diff_counts = {
            item['class_name']: round((item['cell_count'] / total_cells) * 100, 1)
            for item in cell_counts
        }

        return diff_counts

    def get(self, request, case_id, *args, **kwargs):

        diff_counts = self.get_diff(case_id)

        return Response({
            'success': True,
            'diff_counts': diff_counts
        })
        
