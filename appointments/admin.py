from django.contrib import admin

from .models import Appointment


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ["user", "property", "agent", "visit_date", "visit_time", "status"]
    list_filter = ["status", "visit_date"]
    actions = ["confirm", "cancel"]

    @admin.action(description="Mark Confirmed")
    def confirm(self, request, queryset):
        queryset.update(status=Appointment.Status.CONFIRMED)

    @admin.action(description="Mark Cancelled")
    def cancel(self, request, queryset):
        queryset.update(status=Appointment.Status.CANCELLED)
