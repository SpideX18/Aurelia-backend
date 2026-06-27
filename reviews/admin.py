from django.contrib import admin

from .models import PropertyReview, Testimonial


@admin.register(PropertyReview)
class PropertyReviewAdmin(admin.ModelAdmin):
    list_display = ["property", "user", "rating", "is_approved", "created_at"]
    list_filter = ["is_approved"]
    actions = ["approve"]

    @admin.action(description="Approve selected reviews")
    def approve(self, request, queryset):
        queryset.update(is_approved=True)


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ["name", "rating", "is_approved", "created_at"]
    list_filter = ["is_approved"]
    actions = ["approve"]

    @admin.action(description="Approve selected testimonials")
    def approve(self, request, queryset):
        queryset.update(is_approved=True)
