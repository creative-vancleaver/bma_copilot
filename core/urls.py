from django.urls import path, include
from django.contrib.auth import views as auth_views

from . import views
from users import views as users_views

urlpatterns = [
    
    # FRONT END URLS
    path('', views.index, name='home'),

    # path('accounts/', include('django.contrib.auth.urls'), name='accounts'),
    # path('register/', users_views.register_view, name='register'),
    # path('login/', users_views.login_view, name='login'),
    path("register/", users_views.register_user, name="register"),
    path("login/", auth_views.LoginView.as_view(template_name="registration/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),


    path('case/<int:case_id>/', views.case, name="case"),

    path('preview_popup/', views.preview_popup, name='preview_popup'),

]
