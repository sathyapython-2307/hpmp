from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import MedicalReport
from .forms import MedicalReportForm
from patients.models import Patient
from accounts.utils import log_activity
from notifications.models import Notification


@login_required
def report_list(request):
    user = request.user
    if user.is_patient:
        try:
            patient = Patient.objects.get(user=user)
            reports = MedicalReport.objects.filter(patient=patient)
        except Patient.DoesNotExist:
            reports = MedicalReport.objects.none()
    elif user.is_doctor:
        reports = MedicalReport.objects.filter(patient__assigned_doctor=user)
    else:
        reports = MedicalReport.objects.all()
    
    report_type = request.GET.get('type')
    if report_type:
        reports = reports.filter(report_type=report_type)
    
    return render(request, 'reports/report_list.html', {'reports': reports})


@login_required
def patient_reports(request, patient_id):
    patient = get_object_or_404(Patient, pk=patient_id)
    reports = MedicalReport.objects.filter(patient=patient)
    return render(request, 'reports/patient_reports.html', {'patient': patient, 'reports': reports})


@login_required
def upload_report(request, patient_id):
    patient = get_object_or_404(Patient, pk=patient_id)
    if request.user.is_patient:
        messages.error(request, 'Access denied.')
        return redirect('accounts:dashboard')
    
    if request.method == 'POST':
        form = MedicalReportForm(request.POST, request.FILES)
        if form.is_valid():
            report = form.save(commit=False)
            report.patient = patient
            report.uploaded_by = request.user
            report.save()
            
            if patient.user:
                Notification.objects.create(
                    user=patient.user,
                    title='New Medical Report',
                    message=f'A new {report.get_report_type_display()} has been uploaded.',
                    notification_type='info'
                )
            
            log_activity(request.user, 'Report Uploaded', f'Uploaded {report.title} for {patient.full_name}', request)
            messages.success(request, 'Report uploaded successfully!')
            return redirect('reports:patient_reports', patient_id=patient_id)
    else:
        form = MedicalReportForm()
    return render(request, 'reports/report_form.html', {'form': form, 'patient': patient, 'title': 'Upload Report'})


@login_required
def report_detail(request, pk):
    report = get_object_or_404(MedicalReport, pk=pk)
    if request.user.is_patient:
        try:
            patient = Patient.objects.get(user=request.user)
            if report.patient != patient:
                messages.error(request, 'Access denied.')
                return redirect('accounts:dashboard')
        except Patient.DoesNotExist:
            messages.error(request, 'Access denied.')
            return redirect('accounts:dashboard')
    return render(request, 'reports/report_detail.html', {'report': report})


@login_required
def edit_report(request, pk):
    report = get_object_or_404(MedicalReport, pk=pk)
    if request.user.is_patient:
        messages.error(request, 'Access denied.')
        return redirect('accounts:dashboard')
    
    if request.method == 'POST':
        form = MedicalReportForm(request.POST, request.FILES, instance=report)
        if form.is_valid():
            form.save()
            log_activity(request.user, 'Report Updated', f'Updated {report.title}', request)
            messages.success(request, 'Report updated successfully!')
            return redirect('reports:report_detail', pk=pk)
    else:
        form = MedicalReportForm(instance=report)
    return render(request, 'reports/report_form.html', {'form': form, 'patient': report.patient, 'title': 'Edit Report'})


@login_required
def delete_report(request, pk):
    report = get_object_or_404(MedicalReport, pk=pk)
    if request.user.is_patient:
        messages.error(request, 'Access denied.')
        return redirect('accounts:dashboard')
    
    patient_id = report.patient.pk
    if request.method == 'POST':
        report.delete()
        log_activity(request.user, 'Report Deleted', f'Deleted report', request)
        messages.success(request, 'Report deleted successfully!')
        return redirect('reports:patient_reports', patient_id=patient_id)
    return render(request, 'reports/report_confirm_delete.html', {'report': report})
