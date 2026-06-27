from django.conf import settings
from django.db import models


class Agent(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="agent_profile", null=True, blank=True
    )
    name = models.CharField(max_length=150)
    designation = models.CharField(max_length=120, blank=True)
    photo = models.ImageField(upload_to="agents/photos/", blank=True, null=True)
    experience_years = models.PositiveIntegerField(default=0)
    biography = models.TextField(blank=True)

    phone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)

    facebook_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    @property
    def active_listings_count(self):
        return self.properties.filter(is_active=True, is_sold=False).count()

    @property
    def sold_count(self):
        return self.properties.filter(is_sold=True).count()


class AgentReview(models.Model):
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="agent_reviews")
    rating = models.PositiveSmallIntegerField()
    comment = models.TextField(blank=True)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = ("agent", "user")
