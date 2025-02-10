from django.urls import path

from . import views

urlpatterns = [
    
    # FRONT URLS
    path('', views.index, name='home'),

    path('case/<int:case_id>/', views.case, name="case"),

    path('preview_popup/', views.preview_popup, name='preview_popup'),

]
