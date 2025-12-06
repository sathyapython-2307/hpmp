from django.contrib import admin
from .models import MedicalReport


@admin.register(MedicalReport)
class MedicalReportAdmin(admin.ModelAdmin):
    list_display = ['patient', 'title', 'report_type', 'report_date', 'is_critical']
    list_filter = ['report_type', 'is_critical', 'report_date']
    search_fields = ['patient__first_name', 'title']
