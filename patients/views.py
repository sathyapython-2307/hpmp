from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Patient, MedicalHistory, MedicalHistoryFile
from .forms import PatientForm, MedicalHistoryForm, MedicalHistoryFileForm
from accounts.utils import log_activity


@login_required
def patient_list(request):
    user = request.user
    if user.is_patient:
        patients = Patient.objects.filter(user=user)
    elif user.is_doctor:
        patients = Patient.objects.filter(assigned_doctor=user)
    else:
        patients = Patient.objects.all()
    return render(request, 'patients/patient_list.html', {'patients': patients})


@login_required
def patient_detail(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    if request.user.is_patient and patient.user != request.user:
        messages.error(request, 'Access denied.')
        return redirect('accounts:dashboard')
    return render(request, 'patients/patient_detail.html', {'patient': patient})


@login_required
def patient_add(request):
    if request.user.is_patient:
        messages.error(request, 'Patients cannot add other patients.')
        return redirect('accounts:dashboard')
    
    if request.method == 'POST':
        form = PatientForm(request.POST)
        if form.is_valid():
            patient = form.save()
            log_activity(request.user, 'Patient Added', f'Added patient: {patient.full_name}', request)
            messages.success(request, 'Patient added successfully!')
            return redirect('patients:patient_detail', pk=patient.pk)
    else:
        form = PatientForm()
    return render(request, 'patients/patient_form.html', {'form': form, 'title': 'Add Patient'})


@login_required
def patient_edit(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    if request.user.is_patient:
        messages.error(request, 'Access denied.')
        return redirect('accounts:dashboard')
    
    if request.method == 'POST':
        form = PatientForm(request.POST, instance=patient)
        if form.is_valid():
            form.save()
            log_activity(request.user, 'Patient Updated', f'Updated patient: {patient.full_name}', request)
            messages.success(request, 'Patient updated successfully!')
            return redirect('patients:patient_detail', pk=pk)
    else:
        form = PatientForm(instance=patient)
    return render(request, 'patients/patient_form.html', {'form': form, 'title': 'Edit Patient', 'patient': patient})


@login_required
def patient_delete(request, pk):
    if not request.user.is_admin:
        messages.error(request, 'Only admins can delete patients.')
        return redirect('accounts:dashboard')
    
    patient = get_object_or_404(Patient, pk=pk)
    if request.method == 'POST':
        name = patient.full_name
        patient.delete()
        log_activity(request.user, 'Patient Deleted', f'Deleted patient: {name}', request)
        messages.success(request, f'Patient {name} deleted successfully!')
        return redirect('patients:patient_list')
    return render(request, 'patients/patient_confirm_delete.html', {'patient': patient})


@login_required
def add_medical_history(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    if request.user.is_patient:
        messages.error(request, 'Access denied.')
        return redirect('accounts:dashboard')
    
    if request.method == 'POST':
        form = MedicalHistoryForm(request.POST)
        if form.is_valid():
            history = form.save(commit=False)
            history.patient = patient
            history.save()
            log_activity(request.user, 'Medical History Added', f'Added history for: {patient.full_name}', request)
            messages.success(request, 'Medical history added successfully!')
            return redirect('patients:patient_detail', pk=pk)
    else:
        form = MedicalHistoryForm()
    return render(request, 'patients/medical_history_form.html', {'form': form, 'patient': patient})


@login_required
def upload_medical_file(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    if request.user.is_patient:
        messages.error(request, 'Access denied.')
        return redirect('accounts:dashboard')
    
    if request.method == 'POST':
        form = MedicalHistoryFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.save(commit=False)
            file.patient = patient
            file.uploaded_by = request.user
            file.save()
            log_activity(request.user, 'Medical File Uploaded', f'Uploaded file for: {patient.full_name}', request)
            messages.success(request, 'File uploaded successfully!')
            return redirect('patients:patient_detail', pk=pk)
    else:
        form = MedicalHistoryFileForm()
    return render(request, 'patients/upload_file_form.html', {'form': form, 'patient': patient})


@login_required
def delete_medical_file(request, pk):
    file = get_object_or_404(MedicalHistoryFile, pk=pk)
    patient_pk = file.patient.pk
    if request.user.is_patient:
        messages.error(request, 'Access denied.')
        return redirect('accounts:dashboard')
    
    if request.method == 'POST':
        file.delete()
        log_activity(request.user, 'Medical File Deleted', f'Deleted file: {file.title}', request)
        messages.success(request, 'File deleted successfully!')
        return redirect('patients:patient_detail', pk=patient_pk)
    return render(request, 'patients/file_confirm_delete.html', {'file': file})
