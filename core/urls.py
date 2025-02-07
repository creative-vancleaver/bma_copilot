from django.urls import path

from . import views

urlpatterns = [
    
    # FRONT URLS
    path('', views.index, name='home'),

    path('case/<int:case_id>/', views.case, name="case"),

]
