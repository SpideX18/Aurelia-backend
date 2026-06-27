from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("accounts.urls")),
    path("api/", include("properties.urls")),
    path("api/", include("agents.urls")),
    path("api/", include("appointments.urls")),
    path("api/", include("wishlist.urls")),
    path("api/", include("reviews.urls")),
    path("api/analytics/", include("analytics_app.urls")),
    path("api/", include("settings_app.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
