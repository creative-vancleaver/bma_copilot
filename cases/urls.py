from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .import views

router = DefaultRouter()
router.register(r'', views.CaseViewSet)

urlpatterns = [
    path('', include(router.urls)),

    # CASE API VIEWS
    path('<int:case_id>/save-screenshot/', views.save_screenshot, name='save-screenshot'),
    path('<int:case_id>/save-recording/', views.save_recording, name='save-recording'),

]
