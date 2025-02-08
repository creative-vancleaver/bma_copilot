from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
# REGISTER CELLS API VIEW AT /api/cells/
router.register(r'', views.CellViewSet, basename='cell')

urlpatterns = [
    path('', include(router.urls)),

    path('label_cell/', views.LabelCellView.as_view(), name="label_cell"),

    path('stats/<int:case_id>/', views.CellStatsView.as_view(), name='cell_stats'),
    path('cell_counts/<int:case_id>/', views.CellClassCountView.as_view(), name='cell_counts'),
    path('get_diff/<int:case_id>/', views.DifferentialCountView.as_view(), name='get_diff'),

]
