from django.contrib import admin

from .models import Agent, AgentReview


@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    list_display = ["name", "designation", "experience_years", "is_active", "active_listings_count", "sold_count"]
    search_fields = ["name", "email"]


@admin.register(AgentReview)
class AgentReviewAdmin(admin.ModelAdmin):
    list_display = ["agent", "user", "rating", "is_approved", "created_at"]
    list_filter = ["is_approved"]
