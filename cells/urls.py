from django.urls import path, include

from . import views


urlpatterns = [


    path('cell/<str:case_id>/', views.CellView.as_view(), name='cell_api'),
    path('json_cell/<str:case_id>/', views.JSONCellView.as_view(), name='json_cell_api'),

    # path('cell_counts/<int:case_id>/', views.CellClassCountView.as_view(), name='cell_counts'),
    # path('get_diff/<int:case_id>/', views.DifferentialCountView.as_view(), name='get_diff'),
    # path('label_cell/', views.LabelCellView.as_view(), name="label_cell"),

]
