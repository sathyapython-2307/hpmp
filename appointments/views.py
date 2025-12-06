from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Appointment
from .forms import AppointmentForm, PatientAppointmentForm, AppointmentStatusForm
from patients.models import Patient
from accounts.utils import log_activity
from notifications.models import Notification


@login_required
def appointment_list(request):
    user = request.user
    if user.is_patient:
        try:
            patient = Patient.objects.get(user=user)
            appointments = Appointment.objects.filter(patient=patient)
        except Patient.DoesNotExist:
            appointments = Appointment.objects.none()
    elif user.is_doctor:
        appointments = Appointment.objects.filter(doctor=user)
    else:
        appointments = Appointment.objects.all()
    
    status_filter = request.GET.get('status')
    if status_filter:
        appointments = appointments.filter(status=status_filter)
    
    return render(request, 'appointments/appointment_list.html', {'appointments': appointments})


@login_required
def create_appointment(request):
    user = request.user
    
    if user.is_patient:
        try:
            patient = Patient.objects.get(user=user)
        except Patient.DoesNotExist:
            messages.error(request, 'Patient profile not found.')
            return redirect('accounts:dashboard')
        
        if request.method == 'POST':
            form = PatientAppointmentForm(request.POST)
            if form.is_valid():
                appointment = form.save(commit=False)
                appointment.patient = patient
                appointment.created_by = user
                appointment.save()
                
                Notification.objects.create(
                    user=appointment.doctor,
                    title='New Appointment Request',
                    message=f'{patient.full_name} requested an appointment on {appointment.appointment_date}',
                    notification_type='info'
                )
                
                log_activity(user, 'Appointment Created', f'Created appointment with Dr. {appointment.doctor.get_full_name()}', request)
                messages.success(request, 'Appointment request submitted!')
                return redirect('appointments:appointment_list')
        else:
            form = PatientAppointmentForm()
        return render(request, 'appointments/appointment_form.html', {'form': form, 'title': 'Request Appointment'})
    
    else:
        if request.method == 'POST':
            form = AppointmentForm(request.POST, user=user)
            if form.is_valid():
                appointment = form.save(commit=False)
                appointment.created_by = user
                if user.is_receptionist:
                    appointment.status = 'pending'
                appointment.save()
                
                Notification.objects.create(
                    user=appointment.doctor,
                    title='New Appointment',
                    message=f'Appointment scheduled for {appointment.patient.full_name} on {appointment.appointment_date}',
                    notification_type='info'
                )
                
                log_activity(user, 'Appointment Created', f'Created appointment for {appointment.patient.full_name}', request)
                messages.success(request, 'Appointment created successfully!')
                return redirect('appointments:appointment_list')
        else:
            form = AppointmentForm(user=user)
        return render(request, 'appointments/appointment_form.html', {'form': form, 'title': 'Create Appointment'})


@login_required
def appointment_detail(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    return render(request, 'appointments/appointment_detail.html', {'appointment': appointment})


@login_required
def edit_appointment(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    if request.user.is_patient:
        messages.error(request, 'Access denied.')
        return redirect('accounts:dashboard')
    
    if request.method == 'POST':
        form = AppointmentForm(request.POST, instance=appointment, user=request.user)
        if form.is_valid():
            form.save()
            log_activity(request.user, 'Appointment Updated', f'Updated appointment #{pk}', request)
            messages.success(request, 'Appointment updated successfully!')
            return redirect('appointments:appointment_detail', pk=pk)
    else:
        form = AppointmentForm(instance=appointment, user=request.user)
    return render(request, 'appointments/appointment_form.html', {'form': form, 'title': 'Edit Appointment'})


@login_required
def cancel_appointment(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    if request.method == 'POST':
        appointment.status = 'cancelled'
        appointment.save()
        log_activity(request.user, 'Appointment Cancelled', f'Cancelled appointment #{pk}', request)
        messages.success(request, 'Appointment cancelled!')
    return redirect('appointments:appointment_list')


@login_required
def approve_appointment(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    if not request.user.is_doctor and not request.user.is_admin:
        messages.error(request, 'Only doctors can approve appointments.')
        return redirect('accounts:dashboard')
    
    if request.method == 'POST':
        appointment.status = 'approved'
        appointment.save()
        
        if appointment.patient.user:
            Notification.objects.create(
                user=appointment.patient.user,
                title='Appointment Approved',
                message=f'Your appointment on {appointment.appointment_date} has been approved.',
                notification_type='success'
            )
        
        log_activity(request.user, 'Appointment Approved', f'Approved appointment #{pk}', request)
        messages.success(request, 'Appointment approved!')
    return redirect('appointments:appointment_list')


@login_required
def reject_appointment(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    if not request.user.is_doctor and not request.user.is_admin:
        messages.error(request, 'Only doctors can reject appointments.')
        return redirect('accounts:dashboard')
    
    if request.method == 'POST':
        appointment.status = 'rejected'
        appointment.rejection_reason = request.POST.get('reason', '')
        appointment.save()
        
        if appointment.patient.user:
            Notification.objects.create(
                user=appointment.patient.user,
                title='Appointment Rejected',
                message=f'Your appointment on {appointment.appointment_date} has been rejected.',
                notification_type='warning'
            )
        
        log_activity(request.user, 'Appointment Rejected', f'Rejected appointment #{pk}', request)
        messages.success(request, 'Appointment rejected!')
    return redirect('appointments:appointment_list')


@login_required
def complete_appointment(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    if not request.user.is_doctor and not request.user.is_admin:
        messages.error(request, 'Only doctors can complete appointments.')
        return redirect('accounts:dashboard')
    
    if request.method == 'POST':
        appointment.status = 'completed'
        appointment.notes = request.POST.get('notes', '')
        appointment.save()
        log_activity(request.user, 'Appointment Completed', f'Completed appointment #{pk}', request)
        messages.success(request, 'Appointment marked as completed!')
    return redirect('appointments:appointment_list')
