from django.urls import path, include

from . import views

urlpatterns = [
    
    # FRONT END URLS
    path('', views.index, name='home'),

    path('accounts/', include('django.contrib.auth.urls'), name='accounts'),

    path('case/<int:case_id>/', views.case, name="case"),

    path('preview_popup/', views.preview_popup, name='preview_popup'),

]
