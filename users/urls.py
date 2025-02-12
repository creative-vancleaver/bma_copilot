from django.urls import path, include

from users.views import user_login  # Import the login view

urlpatterns = [

    # # path('login/', user_login, name='login'),  # Add this line for login
    # path('accounts/', include('django.contrib.auth.urls'), name='accounts'),
]

