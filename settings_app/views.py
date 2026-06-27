from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny

from accounts.permissions import IsAdminOrSuperAdmin
from .models import SiteSettings
from .serializers import SiteSettingsSerializer


class SiteSettingsView(RetrieveUpdateAPIView):
    serializer_class = SiteSettingsSerializer

    def get_object(self):
        return SiteSettings.load()

    def get_permissions(self):
        if self.request.method in ("GET", "HEAD", "OPTIONS"):
            return [AllowAny()]
        return [IsAdminOrSuperAdmin()]
