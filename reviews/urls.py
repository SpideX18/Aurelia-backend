from rest_framework.routers import DefaultRouter

from .views import PropertyReviewViewSet, TestimonialViewSet

router = DefaultRouter()
router.register("property-reviews", PropertyReviewViewSet, basename="property-review")
router.register("testimonials", TestimonialViewSet, basename="testimonial")

urlpatterns = router.urls
