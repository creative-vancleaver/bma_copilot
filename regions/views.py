from django.shortcuts import render

# Create your views here.
from rest_framework import status, viewsets
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from rest_framework.decorators import action

from .models import Region, RegionImage, RegionClassification
from .serializers import RegionSerializer, RegionImage, RegionClassificationSerializer


class RegionViewSet(viewsets.ModelViewSet):

    authentication_classes = []
    permission_classes = [AllowAny]
    
    queryset = Region.objects.all().order_by('-id')
    serializer_class = RegionSerializer

    def get_queryset(self):
        return Region.objects.select_related(
            'case',
            'video',
            'image',
            # 'classification' -- ONLY WORKS FOR ONE-TO-ONE RELATIONS
        ).prefetch_related(
            'classification' # USED FOR FOREIGN KEY RELATIONS
        ).all().order_by('-id')
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context ['request'] = self.request
        return context
    
    @action(detail=True, methods=['get'])
    def classification_details(self, request, pk=None):
        region = self.get_object()
        if not hasattr(region, 'classification') or region.clasification is None:
            return Response({
                'success': False,
                'message': 'No classification data available for this region.'
            }, status=status.HTTP_404_NOT_FOUND)