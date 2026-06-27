from django.urls import path

from .views import ChartDataView, DashboardStatsView

urlpatterns = [
    path("dashboard-stats/", DashboardStatsView.as_view(), name="dashboard-stats"),
    path("chart-data/", ChartDataView.as_view(), name="chart-data"),
]
