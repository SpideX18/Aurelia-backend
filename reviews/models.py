from django.conf import settings
from django.db import models


class PropertyReview(models.Model):
    property = models.ForeignKey("properties.Property", on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="property_reviews")
    rating = models.PositiveSmallIntegerField()
    comment = models.TextField(blank=True)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = ("property", "user")

    def __str__(self):
        return f"{self.rating}* on {self.property}"


class Testimonial(models.Model):
    """Standalone homepage testimonials, distinct from per-property reviews."""

    name = models.CharField(max_length=150)
    location = models.CharField(max_length=150, blank=True)
    photo = models.ImageField(upload_to="testimonials/", blank=True, null=True)
    rating = models.PositiveSmallIntegerField(default=5)
    text = models.TextField()
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Testimonial - {self.name}"
