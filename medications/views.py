from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Medication, Treatment
from .forms import MedicationForm, TreatmentForm
from patients.models import Patient
from accounts.utils import log_activity
from notifications.models import Notification


@login_required
def medication_list(request):
    if request.user.is_patient:
        try:
            patient = Patient.objects.get(user=request.user)
            medications = Medication.objects.filter(patient=patient)
        except Patient.DoesNotExist:
            medications = Medication.objects.none()
    elif request.user.is_doctor:
        medications = Medication.objects.filter(patient__assigned_doctor=request.user)
    else:
        medications = Medication.objects.all()
    return render(request, 'medications/medication_list.html', {'medications': medications})


@login_required
def patient_medications(request, patient_id):
    patient = get_object_or_404(Patient, pk=patient_id)
    medications = Medication.objects.filter(patient=patient)
    treatments = Treatment.objects.filter(patient=patient)
    return render(request, 'medications/patient_medications.html', {
        'patient': patient, 'medications': medications, 'treatments': treatments
    })


@login_required
def add_medication(request, patient_id):
    patient = get_object_or_404(Patient, pk=patient_id)
    if not request.user.is_doctor and not request.user.is_admin:
        messages.error(request, 'Only doctors can prescribe medications.')
        return redirect('accounts:dashboard')
    
    if request.method == 'POST':
        form = MedicationForm(request.POST)
        if form.is_valid():
            medication = form.save(commit=False)
            medication.patient = patient
            medication.prescribed_by = request.user
            medication.save()
            
            Notification.objects.create(
                user=patient.user if patient.user else request.user,
                title='New Medication Prescribed',
                message=f'{medication.medicine_name} has been prescribed.',
                notification_type='info'
            )
            
            log_activity(request.user, 'Medication Prescribed', f'Prescribed {medication.medicine_name} for {patient.full_name}', request)
            messages.success(request, 'Medication prescribed successfully!')
            return redirect('medications:patient_medications', patient_id=patient_id)
    else:
        form = MedicationForm()
    return render(request, 'medications/medication_form.html', {'form': form, 'patient': patient, 'title': 'Prescribe Medication'})


@login_required
def edit_medication(request, pk):
    medication = get_object_or_404(Medication, pk=pk)
    if not request.user.is_doctor and not request.user.is_admin:
        messages.error(request, 'Access denied.')
        return redirect('accounts:dashboard')
    
    if request.method == 'POST':
        form = MedicationForm(request.POST, instance=medication)
        if form.is_valid():
            form.save()
            log_activity(request.user, 'Medication Updated', f'Updated {medication.medicine_name}', request)
            messages.success(request, 'Medication updated successfully!')
            return redirect('medications:patient_medications', patient_id=medication.patient.pk)
    else:
        form = MedicationForm(instance=medication)
    return render(request, 'medications/medication_form.html', {'form': form, 'patient': medication.patient, 'title': 'Edit Medication'})


@login_required
def delete_medication(request, pk):
    medication = get_object_or_404(Medication, pk=pk)
    if not request.user.is_doctor and not request.user.is_admin:
        messages.error(request, 'Access denied.')
        return redirect('accounts:dashboard')
    
    patient_id = medication.patient.pk
    if request.method == 'POST':
        medication.delete()
        log_activity(request.user, 'Medication Deleted', f'Deleted medication', request)
        messages.success(request, 'Medication deleted successfully!')
        return redirect('medications:patient_medications', patient_id=patient_id)
    return render(request, 'medications/medication_confirm_delete.html', {'medication': medication})


@login_required
def mark_taken(request, pk):
    medication = get_object_or_404(Medication, pk=pk)
    if not request.user.is_nurse and not request.user.is_doctor and not request.user.is_admin:
        messages.error(request, 'Only nurses or doctors can mark medications as taken.')
        return redirect('accounts:dashboard')
    
    if request.method == 'POST':
        medication.is_taken = True
        medication.taken_at = timezone.now()
        medication.administered_by = request.user
        medication.save()
        log_activity(request.user, 'Medication Administered', f'Administered {medication.medicine_name} to {medication.patient.full_name}', request)
        messages.success(request, 'Medication marked as taken!')
    return redirect('medications:patient_medications', patient_id=medication.patient.pk)


@login_required
def treatment_list(request):
    if request.user.is_patient:
        try:
            patient = Patient.objects.get(user=request.user)
            treatments = Treatment.objects.filter(patient=patient)
        except Patient.DoesNotExist:
            treatments = Treatment.objects.none()
    elif request.user.is_doctor:
        treatments = Treatment.objects.filter(doctor=request.user)
    else:
        treatments = Treatment.objects.all()
    return render(request, 'medications/treatment_list.html', {'treatments': treatments})


@login_required
def add_treatment(request, patient_id):
    patient = get_object_or_404(Patient, pk=patient_id)
    if not request.user.is_doctor and not request.user.is_admin:
        messages.error(request, 'Only doctors can add treatments.')
        return redirect('accounts:dashboard')
    
    if request.method == 'POST':
        form = TreatmentForm(request.POST)
        if form.is_valid():
            treatment = form.save(commit=False)
            treatment.patient = patient
            treatment.doctor = request.user
            treatment.save()
            log_activity(request.user, 'Treatment Added', f'Added treatment for {patient.full_name}', request)
            messages.success(request, 'Treatment added successfully!')
            return redirect('medications:patient_medications', patient_id=patient_id)
    else:
        form = TreatmentForm()
    return render(request, 'medications/treatment_form.html', {'form': form, 'patient': patient})


@login_required
def edit_treatment(request, pk):
    treatment = get_object_or_404(Treatment, pk=pk)
    if not request.user.is_doctor and not request.user.is_admin:
        messages.error(request, 'Access denied.')
        return redirect('accounts:dashboard')
    
    if request.method == 'POST':
        form = TreatmentForm(request.POST, instance=treatment)
        if form.is_valid():
            form.save()
            log_activity(request.user, 'Treatment Updated', f'Updated treatment', request)
            messages.success(request, 'Treatment updated successfully!')
            return redirect('medications:patient_medications', patient_id=treatment.patient.pk)
    else:
        form = TreatmentForm(instance=treatment)
    return render(request, 'medications/treatment_form.html', {'form': form, 'patient': treatment.patient})
