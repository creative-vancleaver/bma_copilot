from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('preview_modal/', views.preview, name='preview'),
]
