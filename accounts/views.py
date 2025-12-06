from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.db.models import Count
from .models import User, DoctorProfile, NurseProfile, ActivityLog
from .forms import LoginForm, UserRegistrationForm, UserUpdateForm, DoctorProfileForm, NurseProfileForm
from .utils import log_activity


class CustomLoginView(LoginView):
    form_class = LoginForm
    template_name = 'accounts/login.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        log_activity(self.request.user, 'Login', 'User logged in', self.request)
        return response


@login_required
def logout_view(request):
    log_activity(request.user, 'Logout', 'User logged out', request)
    logout(request)
    return redirect('accounts:login')


@login_required
def dashboard(request):
    from patients.models import Patient
    from appointments.models import Appointment
    from vitals.models import VitalSign, VitalAlert
    from medications.models import Medication
    
    user = request.user
    context = {'user': user}
    
    if user.is_admin:
        context.update({
            'total_patients': Patient.objects.count(),
            'total_doctors': User.objects.filter(role='doctor').count(),
            'total_nurses': User.objects.filter(role='nurse').count(),
            'total_appointments': Appointment.objects.count(),
            'pending_appointments': Appointment.objects.filter(status='pending').count(),
            'recent_activities': ActivityLog.objects.all()[:10],
            'active_alerts': VitalAlert.objects.filter(is_resolved=False).count(),
        })
        return render(request, 'accounts/dashboard_admin.html', context)
    
    elif user.is_doctor:
        doctor_patients = Patient.objects.filter(assigned_doctor=user)
        context.update({
            'my_patients': doctor_patients,
            'my_patients_count': doctor_patients.count(),
            'pending_appointments': Appointment.objects.filter(doctor=user, status='pending'),
            'today_appointments': Appointment.objects.filter(doctor=user, status='approved'),
            'active_alerts': VitalAlert.objects.filter(patient__assigned_doctor=user, is_resolved=False),
        })
        return render(request, 'accounts/dashboard_doctor.html', context)
    
    elif user.is_nurse:
        context.update({
            'patients': Patient.objects.all()[:20],
            'pending_medications': Medication.objects.filter(is_taken=False),
            'active_alerts': VitalAlert.objects.filter(is_resolved=False),
            'recent_vitals': VitalSign.objects.all()[:10],
        })
        return render(request, 'accounts/dashboard_nurse.html', context)
    
    elif user.is_receptionist:
        context.update({
            'pending_appointments': Appointment.objects.filter(status='pending'),
            'today_appointments': Appointment.objects.filter(status='approved'),
            'total_patients': Patient.objects.count(),
            'recent_patients': Patient.objects.all()[:10],
        })
        return render(request, 'accounts/dashboard_receptionist.html', context)
    
    else:  # Patient
        try:
            patient = Patient.objects.get(user=user)
            context.update({
                'patient': patient,
                'my_appointments': Appointment.objects.filter(patient=patient),
                'my_vitals': VitalSign.objects.filter(patient=patient)[:10],
                'my_medications': Medication.objects.filter(patient=patient),
                'my_alerts': VitalAlert.objects.filter(patient=patient),
            })
        except Patient.DoesNotExist:
            context['patient'] = None
        return render(request, 'accounts/dashboard_patient.html', context)


@login_required
def register_user(request):
    if not request.user.is_admin:
        messages.error(request, 'Only admins can register new users.')
        return redirect('accounts:dashboard')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            log_activity(request.user, 'User Registration', f'Registered user: {user.username}', request)
            messages.success(request, f'User {user.username} created successfully!')
            return redirect('accounts:user_list')
    else:
        form = UserRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})


@login_required
def user_list(request):
    if not request.user.is_admin:
        messages.error(request, 'Access denied.')
        return redirect('accounts:dashboard')
    users = User.objects.all().order_by('-created_at')
    return render(request, 'accounts/user_list.html', {'users': users})


@login_required
def user_detail(request, pk):
    user = get_object_or_404(User, pk=pk)
    if not request.user.is_admin and request.user != user:
        messages.error(request, 'Access denied.')
        return redirect('accounts:dashboard')
    return render(request, 'accounts/user_detail.html', {'profile_user': user})


@login_required
def user_edit(request, pk):
    user = get_object_or_404(User, pk=pk)
    if not request.user.is_admin and request.user != user:
        messages.error(request, 'Access denied.')
        return redirect('accounts:dashboard')
    
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            log_activity(request.user, 'User Update', f'Updated user: {user.username}', request)
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:user_detail', pk=pk)
    else:
        form = UserUpdateForm(instance=user)
    return render(request, 'accounts/user_edit.html', {'form': form, 'profile_user': user})


@login_required
def user_delete(request, pk):
    if not request.user.is_admin:
        messages.error(request, 'Only admins can delete users.')
        return redirect('accounts:dashboard')
    
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        username = user.username
        user.delete()
        log_activity(request.user, 'User Deletion', f'Deleted user: {username}', request)
        messages.success(request, f'User {username} deleted successfully!')
        return redirect('accounts:user_list')
    return render(request, 'accounts/user_confirm_delete.html', {'profile_user': user})


@login_required
def activity_logs(request):
    if not request.user.is_admin:
        messages.error(request, 'Access denied.')
        return redirect('accounts:dashboard')
    logs = ActivityLog.objects.all()[:100]
    return render(request, 'accounts/activity_logs.html', {'logs': logs})


@login_required
def profile(request):
    return render(request, 'accounts/profile.html', {'profile_user': request.user})
