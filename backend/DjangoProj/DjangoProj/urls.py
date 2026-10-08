from django.urls import path, include
from api.media import media_serve
from api.adminsite import custom_admin_site

urlpatterns = [
    path('admin/', custom_admin_site.urls),
    path('api/', include('api.urls')),
    path('media/<path:path>', media_serve),
]