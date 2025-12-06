from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from .models import VitalSign, VitalAlert
from .forms import VitalSignForm
from patients.models import Patient
from accounts.utils import log_activity
from notifications.models import Notification


@login_required
def vitals_list(request):
    if request.user.is_patient:
        try:
            patient = Patient.objects.get(user=request.user)
            vitals = VitalSign.objects.filter(patient=patient)
        except Patient.DoesNotExist:
            vitals = VitalSign.objects.none()
    elif request.user.is_doctor:
        vitals = VitalSign.objects.filter(patient__assigned_doctor=request.user)
    else:
        vitals = VitalSign.objects.all()
    return render(request, 'vitals/vitals_list.html', {'vitals': vitals[:50]})


@login_required
def patient_vitals(request, patient_id):
    patient = get_object_or_404(Patient, pk=patient_id)
    vitals = VitalSign.objects.filter(patient=patient)[:30]
    return render(request, 'vitals/patient_vitals.html', {'patient': patient, 'vitals': vitals})


@login_required
def add_vital(request, patient_id):
    patient = get_object_or_404(Patient, pk=patient_id)
    if request.user.is_patient:
        messages.error(request, 'Access denied.')
        return redirect('accounts:dashboard')
    
    if request.method == 'POST':
        form = VitalSignForm(request.POST)
        if form.is_valid():
            vital = form.save(commit=False)
            vital.patient = patient
            vital.recorded_by = request.user
            vital.save()
            
            # Check for abnormal vitals and create alerts
            abnormals = vital.check_abnormal()
            for param, value, normal in abnormals:
                severity = 'high' if param in ['SpO2', 'Heart Rate'] else 'medium'
                alert = VitalAlert.objects.create(
                    patient=patient,
                    vital_sign=vital,
                    parameter=param,
                    value=str(value),
                    normal_range=normal,
                    severity=severity,
                    message=f"Abnormal {param}: {value} (Normal: {normal})"
                )
                # Create notification for doctor
                if patient.assigned_doctor:
                    Notification.objects.create(
                        user=patient.assigned_doctor,
                        title=f"Vital Alert: {patient.full_name}",
                        message=alert.message,
                        notification_type='alert'
                    )
            
            log_activity(request.user, 'Vital Recorded', f'Recorded vitals for: {patient.full_name}', request)
            messages.success(request, 'Vital signs recorded successfully!')
            if abnormals:
                messages.warning(request, f'{len(abnormals)} abnormal vital(s) detected!')
            return redirect('vitals:patient_vitals', patient_id=patient_id)
    else:
        form = VitalSignForm()
    return render(request, 'vitals/add_vital.html', {'form': form, 'patient': patient})


@login_required
def vitals_chart(request, patient_id):
    patient = get_object_or_404(Patient, pk=patient_id)
    return render(request, 'vitals/vitals_chart.html', {'patient': patient})


@login_required
def vitals_chart_data(request, patient_id):
    patient = get_object_or_404(Patient, pk=patient_id)
    vitals = VitalSign.objects.filter(patient=patient).order_by('recorded_at')[:50]
    
    data = {
        'labels': [v.recorded_at.strftime('%m/%d %H:%M') for v in vitals],
        'heart_rate': [v.heart_rate for v in vitals],
        'systolic_bp': [v.systolic_bp for v in vitals],
        'diastolic_bp': [v.diastolic_bp for v in vitals],
        'temperature': [float(v.temperature) for v in vitals],
        'spo2': [v.spo2 for v in vitals],
        'glucose': [v.glucose if v.glucose else None for v in vitals],
        'respiration': [v.respiration_rate if v.respiration_rate else None for v in vitals],
    }
    return JsonResponse(data)


@login_required
def alerts_list(request):
    if request.user.is_patient:
        try:
            patient = Patient.objects.get(user=request.user)
            alerts = VitalAlert.objects.filter(patient=patient)
        except Patient.DoesNotExist:
            alerts = VitalAlert.objects.none()
    elif request.user.is_doctor:
        alerts = VitalAlert.objects.filter(patient__assigned_doctor=request.user)
    else:
        alerts = VitalAlert.objects.all()
    return render(request, 'vitals/alerts_list.html', {'alerts': alerts[:50]})


@login_required
def resolve_alert(request, pk):
    alert = get_object_or_404(VitalAlert, pk=pk)
    if request.user.is_patient:
        messages.error(request, 'Access denied.')
        return redirect('accounts:dashboard')
    
    if request.method == 'POST':
        alert.is_resolved = True
        alert.resolved_by = request.user
        alert.resolved_at = timezone.now()
        alert.save()
        log_activity(request.user, 'Alert Resolved', f'Resolved alert for: {alert.patient.full_name}', request)
        messages.success(request, 'Alert resolved successfully!')
    return redirect('vitals:alerts_list')
