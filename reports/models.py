from django.db import models
from patients.models import Patient
from accounts.models import User


class MedicalReport(models.Model):
    REPORT_TYPE_CHOICES = [
        ('lab', 'Lab Report'),
        ('prescription', 'Prescription'),
        ('scan', 'Scan Report'),
        ('xray', 'X-Ray'),
        ('mri', 'MRI'),
        ('ct', 'CT Scan'),
        ('ultrasound', 'Ultrasound'),
        ('ecg', 'ECG'),
        ('other', 'Other'),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='medical_reports')
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=200)
    report_type = models.CharField(max_length=20, choices=REPORT_TYPE_CHOICES)
    file = models.FileField(upload_to='reports/')
    description = models.TextField(blank=True)
    report_date = models.DateField()
    findings = models.TextField(blank=True)
    doctor_notes = models.TextField(blank=True)
    is_critical = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-report_date']

    def __str__(self):
        return f"{self.patient.full_name} - {self.title}"
