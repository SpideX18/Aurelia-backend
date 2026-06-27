from django.db.models import Count
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsAdminOrSuperAdmin
from agents.models import Agent
from appointments.models import Appointment
from properties.models import Property
from reviews.models import PropertyReview, Testimonial
from .models import PropertyView

User = get_user_model()


class DashboardStatsView(APIView):
    """Top-line numbers for admin dashboard cards."""

    permission_classes = [IsAdminOrSuperAdmin]

    def get(self, request):
        return Response({
            "total_properties": Property.objects.count(),
            "active_listings": Property.objects.filter(is_active=True, is_sold=False).count(),
            "sold_properties": Property.objects.filter(is_sold=True).count(),
            "featured_properties": Property.objects.filter(is_featured=True).count(),
            "total_agents": Agent.objects.filter(is_active=True).count(),
            "total_customers": User.objects.filter(role="customer").count(),
            "total_appointments": Appointment.objects.count(),
            "pending_appointments": Appointment.objects.filter(status="pending").count(),
            "total_reviews": PropertyReview.objects.count(),
            "pending_testimonials": Testimonial.objects.filter(is_approved=False).count(),
        })


class ChartDataView(APIView):
    """Chart.js-ready datasets: views over time, most-viewed properties, popular locations, appointment status breakdown."""

    permission_classes = [IsAdminOrSuperAdmin]

    def get(self, request):
        most_viewed = (
            Property.objects.order_by("-views_count").values("id", "title", "views_count")[:5]
        )
        popular_locations = (
            Property.objects.values("city").annotate(count=Count("id")).order_by("-count")[:6]
        )
        appointment_stats = (
            Appointment.objects.values("status").annotate(count=Count("id"))
        )
        views_by_day = (
            PropertyView.objects.extra({"day": "date(created_at)"}).values("day").annotate(count=Count("id")).order_by("day")[:30]
        )
        return Response({
            "most_viewed_properties": list(most_viewed),
            "popular_locations": list(popular_locations),
            "appointment_stats": list(appointment_stats),
            "views_by_day": list(views_by_day),
        })
