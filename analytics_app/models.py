from django.conf import settings
from django.db import models


class PropertyView(models.Model):
    """One row per property view event. Drives 'most viewed' / 'popular locations' charts."""

    property = models.ForeignKey("properties.Property", on_delete=models.CASCADE, related_name="view_events")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="property_views"
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["created_at"])]
