from django.urls import path

from . import views
from cases import views as case_views

urlpatterns = [
    path('', views.index, name='home'),

    # FRONT END CASE VIEWS
    path('case/<int:case_id>/', case_views.case, name="case"),

    # path('preview_modal/', views.preview, name='preview'),
]
