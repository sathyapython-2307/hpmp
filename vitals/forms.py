from django import forms
from .models import VitalSign


class VitalSignForm(forms.ModelForm):
    class Meta:
        model = VitalSign
        fields = ['heart_rate', 'systolic_bp', 'diastolic_bp', 'temperature', 'spo2', 'glucose', 'respiration_rate', 'notes']
        widgets = {
            'heart_rate': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'BPM'}),
            'systolic_bp': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'mmHg'}),
            'diastolic_bp': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'mmHg'}),
            'temperature': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'placeholder': '°F'}),
            'spo2': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '%'}),
            'glucose': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'mg/dL'}),
            'respiration_rate': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'breaths/min'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
