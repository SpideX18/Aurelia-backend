from django.contrib import admin

from .models import (
    Amenity, FloorPlan, Property, PropertyComparison, PropertyDocument,
    PropertyImage, PropertyVideo, RecentlyViewed, RecentSearch, SavedSearch,
)


class PropertyImageInline(admin.TabularInline):
    model = PropertyImage
    extra = 1


class PropertyVideoInline(admin.TabularInline):
    model = PropertyVideo
    extra = 0


class FloorPlanInline(admin.TabularInline):
    model = FloorPlan
    extra = 0


class PropertyDocumentInline(admin.TabularInline):
    model = PropertyDocument
    extra = 0


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ["title", "property_type", "listing_status", "price", "city", "is_featured", "is_sold", "created_at"]
    list_filter = ["property_type", "listing_status", "is_featured", "is_sold", "city"]
    search_fields = ["title", "city", "address"]
    prepopulated_fields = {"slug": ("title",)}
    inlines = [PropertyImageInline, PropertyVideoInline, FloorPlanInline, PropertyDocumentInline]
    actions = ["mark_featured", "mark_sold", "bulk_delete_action"]

    @admin.action(description="Mark selected as featured")
    def mark_featured(self, request, queryset):
        queryset.update(is_featured=True)

    @admin.action(description="Mark selected as sold")
    def mark_sold(self, request, queryset):
        queryset.update(is_sold=True)

    @admin.action(description="Delete selected (bulk)")
    def bulk_delete_action(self, request, queryset):
        queryset.delete()


admin.site.register(Amenity)
admin.site.register(SavedSearch)
admin.site.register(RecentSearch)
admin.site.register(RecentlyViewed)
admin.site.register(PropertyComparison)
