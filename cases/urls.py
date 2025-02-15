from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .import views

router = DefaultRouter()
router.register(r'', views.CaseViewSet)

urlpatterns = [
    path('', include(router.urls)),

    # CASE API VIEWS
    path('<str:case_id>/save-screenshot/', views.save_screenshot, name='save-screenshot'),
    path('<str:case_id>/save-recording/', views.save_recording, name='save-recording'),
    path('<str:case_id>/update-status/', views.update_case_status, name='update_case_status'),

]
