from django.urls import path, include

from .import views


urlpatterns = [

    # CASE API VIEWS
    # path('<str:case_id>/save-screenshot/', views.save_screenshot, name='save-screenshot'),
    # path('<str:case_id>/save-recording/', views.save_recording, name='save-recording'),
    path('save-recording/', views.save_recording, name='save-recording'),

    path('video-status/', views.VideoStatusView.as_view(), name='video-status'),
    path('video-status/<str:video_id>/', views.VideoStatusView.as_view(), name='get-video-status'),

    path('<str:case_id>/update-status/', views.update_case_status, name='update_case_status'),

]
