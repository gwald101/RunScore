from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('users.urls')),
    path('strava/', include('strava_integration.urls')),
    path('', include('dashboard.urls')),
]
