from rest_framework.routers import DefaultRouter

from .views import AgentReviewViewSet, AgentViewSet

router = DefaultRouter()
router.register("agents", AgentViewSet, basename="agent")
router.register("agent-reviews", AgentReviewViewSet, basename="agent-review")

urlpatterns = router.urls
