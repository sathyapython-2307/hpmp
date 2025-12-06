from django.db import models
from patients.models import Patient
from accounts.models import User


class VitalSign(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='vital_signs')
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    heart_rate = models.PositiveIntegerField(help_text='BPM')
    systolic_bp = models.PositiveIntegerField(help_text='mmHg')
    diastolic_bp = models.PositiveIntegerField(help_text='mmHg')
    temperature = models.DecimalField(max_digits=4, decimal_places=1, help_text='°F')
    spo2 = models.PositiveIntegerField(help_text='%')
    glucose = models.PositiveIntegerField(help_text='mg/dL', null=True, blank=True)
    respiration_rate = models.PositiveIntegerField(help_text='breaths/min', null=True, blank=True)
    notes = models.TextField(blank=True)
    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-recorded_at']

    def __str__(self):
        return f"{self.patient.full_name} - {self.recorded_at}"

    @property
    def bp_display(self):
        return f"{self.systolic_bp}/{self.diastolic_bp}"

    def check_abnormal(self):
        alerts = []
        if self.heart_rate < 60 or self.heart_rate > 100:
            alerts.append(('Heart Rate', self.heart_rate, '60-100 BPM'))
        if self.systolic_bp < 90 or self.systolic_bp > 140:
            alerts.append(('Systolic BP', self.systolic_bp, '90-140 mmHg'))
        if self.diastolic_bp < 60 or self.diastolic_bp > 90:
            alerts.append(('Diastolic BP', self.diastolic_bp, '60-90 mmHg'))
        if float(self.temperature) < 97.0 or float(self.temperature) > 99.5:
            alerts.append(('Temperature', self.temperature, '97.0-99.5 °F'))
        if self.spo2 < 95:
            alerts.append(('SpO2', self.spo2, '≥95%'))
        if self.glucose and (self.glucose < 70 or self.glucose > 140):
            alerts.append(('Glucose', self.glucose, '70-140 mg/dL'))
        if self.respiration_rate and (self.respiration_rate < 12 or self.respiration_rate > 20):
            alerts.append(('Respiration', self.respiration_rate, '12-20 breaths/min'))
        return alerts


class VitalAlert(models.Model):
    SEVERITY_CHOICES = [('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('critical', 'Critical')]
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='vital_alerts')
    vital_sign = models.ForeignKey(VitalSign, on_delete=models.CASCADE, related_name='alerts')
    parameter = models.CharField(max_length=50)
    value = models.CharField(max_length=50)
    normal_range = models.CharField(max_length=50)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='medium')
    message = models.TextField()
    is_resolved = models.BooleanField(default=False)
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='resolved_alerts')
    resolved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.patient.full_name} - {self.parameter} Alert"
