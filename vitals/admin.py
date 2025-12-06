from django.contrib import admin
from .models import VitalSign, VitalAlert


@admin.register(VitalSign)
class VitalSignAdmin(admin.ModelAdmin):
    list_display = ['patient', 'heart_rate', 'bp_display', 'temperature', 'spo2', 'recorded_at']
    list_filter = ['recorded_at']
    search_fields = ['patient__first_name', 'patient__last_name']


@admin.register(VitalAlert)
class VitalAlertAdmin(admin.ModelAdmin):
    list_display = ['patient', 'parameter', 'severity', 'is_resolved', 'created_at']
    list_filter = ['severity', 'is_resolved', 'created_at']
