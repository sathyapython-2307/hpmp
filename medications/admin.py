from django.contrib import admin
from .models import Medication, Treatment


@admin.register(Medication)
class MedicationAdmin(admin.ModelAdmin):
    list_display = ['patient', 'medicine_name', 'dosage', 'frequency', 'status', 'is_taken']
    list_filter = ['status', 'is_taken', 'frequency']
    search_fields = ['patient__first_name', 'medicine_name']


@admin.register(Treatment)
class TreatmentAdmin(admin.ModelAdmin):
    list_display = ['patient', 'treatment_name', 'doctor', 'scheduled_date', 'status']
    list_filter = ['status', 'scheduled_date']
