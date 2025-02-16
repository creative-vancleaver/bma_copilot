from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
# from users.views import user_login  # Import the login view


urlpatterns = [

    path('admin/', admin.site.urls),

    # HOME PAGE
    path('', include('core.urls')),

    # API PATHS
    path('api/cases/', include('cases.urls')),
    path('api/regions/', include('regions.urls')),
    path('api/cells/', include('cells.urls')),

    # # path('login/', user_login, name='login'),  # Add this line for login
    # path('accounts/', include('django.contrib.auth.urls'), name='accounts'),
]

# SERVE MEDIA FILE IN DEV
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
