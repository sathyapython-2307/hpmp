from django import forms
from .models import MedicalReport


class MedicalReportForm(forms.ModelForm):
    class Meta:
        model = MedicalReport
        fields = ['title', 'report_type', 'file', 'description', 'report_date', 'findings', 'doctor_notes', 'is_critical']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'report_type': forms.Select(attrs={'class': 'form-control'}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'report_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'findings': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'doctor_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_critical': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
