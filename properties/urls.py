from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AmenityViewSet,
    PropertyComparisonView,
    PropertyViewSet,
    RecentlyViewedListView,
    RecentSearchListView,
    SavedSearchViewSet,
)

router = DefaultRouter()
router.register("properties", PropertyViewSet, basename="property")
router.register("amenities", AmenityViewSet, basename="amenity")
router.register("saved-searches", SavedSearchViewSet, basename="saved-search")

urlpatterns = [
    path("", include(router.urls)),
    path("recent-searches/", RecentSearchListView.as_view(), name="recent-searches"),
    path("recently-viewed/", RecentlyViewedListView.as_view(), name="recently-viewed"),
    path("comparison/", PropertyComparisonView.as_view(), name="comparison"),
]
