from django.contrib import admin
from .models import Patient, MedicalHistory, MedicalHistoryFile


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ['patient_id', 'first_name', 'last_name', 'gender', 'status', 'assigned_doctor']
    list_filter = ['status', 'gender', 'blood_group']
    search_fields = ['patient_id', 'first_name', 'last_name', 'phone', 'email']


@admin.register(MedicalHistory)
class MedicalHistoryAdmin(admin.ModelAdmin):
    list_display = ['patient', 'condition', 'diagnosis_date', 'is_current']
    list_filter = ['is_current', 'diagnosis_date']


@admin.register(MedicalHistoryFile)
class MedicalHistoryFileAdmin(admin.ModelAdmin):
    list_display = ['patient', 'title', 'uploaded_by', 'uploaded_at']
