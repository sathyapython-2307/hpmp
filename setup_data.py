#!/usr/bin/env python
"""Script to create sample data for the Healthcare Portal."""
import os
import sys
import django
from datetime import date, datetime, timedelta
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'healthcare_portal.settings')
django.setup()

from django.contrib.auth import get_user_model
from accounts.models import DoctorProfile, NurseProfile
from patients.models import Patient, MedicalHistory
from vitals.models import VitalSign, VitalAlert
from medications.models import Medication, Treatment
from appointments.models import Appointment
from reports.models import MedicalReport
from notifications.models import Notification

User = get_user_model()

def create_users():
    print("Creating users...")
    # Admin
    admin, _ = User.objects.get_or_create(username='admin', defaults={
        'email': 'admin@hospital.com', 'first_name': 'System', 'last_name': 'Admin',
        'role': 'admin', 'is_staff': True, 'is_superuser': True
    })
    admin.set_password('admin123')
    admin.save()
    
    # Doctors
    dr_smith, _ = User.objects.get_or_create(username='dr_smith', defaults={
        'email': 'smith@hospital.com', 'first_name': 'John', 'last_name': 'Smith',
        'role': 'doctor', 'phone': '555-0101'
    })
    dr_smith.set_password('doctor123')
    dr_smith.save()
    DoctorProfile.objects.get_or_create(user=dr_smith, defaults={
        'specialization': 'Cardiology', 'license_number': 'MD12345',
        'department': 'Cardiology', 'experience_years': 15, 'consultation_fee': Decimal('150.00')
    })
    
    dr_jones, _ = User.objects.get_or_create(username='dr_jones', defaults={
        'email': 'jones@hospital.com', 'first_name': 'Sarah', 'last_name': 'Jones',
        'role': 'doctor', 'phone': '555-0102'
    })
    dr_jones.set_password('doctor123')
    dr_jones.save()
    DoctorProfile.objects.get_or_create(user=dr_jones, defaults={
        'specialization': 'General Medicine', 'license_number': 'MD12346',
        'department': 'General', 'experience_years': 10, 'consultation_fee': Decimal('100.00')
    })
    
    # Nurses
    nurse_mary, _ = User.objects.get_or_create(username='nurse_mary', defaults={
        'email': 'mary@hospital.com', 'first_name': 'Mary', 'last_name': 'Johnson',
        'role': 'nurse', 'phone': '555-0201'
    })
    nurse_mary.set_password('nurse123')
    nurse_mary.save()
    NurseProfile.objects.get_or_create(user=nurse_mary, defaults={
        'department': 'ICU', 'shift': 'morning', 'license_number': 'RN54321'
    })
    
    # Receptionist
    reception, _ = User.objects.get_or_create(username='reception', defaults={
        'email': 'reception@hospital.com', 'first_name': 'Lisa', 'last_name': 'Brown',
        'role': 'receptionist', 'phone': '555-0301'
    })
    reception.set_password('reception123')
    reception.save()
    
    # Patient users
    patient_user1, _ = User.objects.get_or_create(username='patient1', defaults={
        'email': 'patient1@email.com', 'first_name': 'Robert', 'last_name': 'Davis',
        'role': 'patient', 'phone': '555-1001'
    })
    patient_user1.set_password('patient123')
    patient_user1.save()
    
    return dr_smith, dr_jones, patient_user1

def create_patients(dr_smith, dr_jones, patient_user1):
    print("Creating patients...")
    patient1, _ = Patient.objects.get_or_create(patient_id='P000001', defaults={
        'user': patient_user1, 'first_name': 'Robert', 'last_name': 'Davis',
        'date_of_birth': date(1985, 5, 15), 'gender': 'M', 'blood_group': 'A+',
        'phone': '555-1001', 'email': 'robert@email.com',
        'address': '123 Main St, City', 'emergency_contact_name': 'Jane Davis',
        'emergency_contact_phone': '555-1002', 'assigned_doctor': dr_smith, 'status': 'active'
    })

    patient2, _ = Patient.objects.get_or_create(patient_id='P000002', defaults={
        'first_name': 'Emily', 'last_name': 'Clark',
        'date_of_birth': date(1990, 8, 22), 'gender': 'F', 'blood_group': 'B+',
        'phone': '555-1003', 'email': 'emily@email.com',
        'address': '456 Oak Ave, City', 'emergency_contact_name': 'Mike Clark',
        'emergency_contact_phone': '555-1004', 'assigned_doctor': dr_jones, 'status': 'active'
    })
    
    patient3, _ = Patient.objects.get_or_create(patient_id='P000003', defaults={
        'first_name': 'James', 'last_name': 'Wilson',
        'date_of_birth': date(1978, 3, 10), 'gender': 'M', 'blood_group': 'O+',
        'phone': '555-1005', 'email': 'james@email.com',
        'address': '789 Pine Rd, City', 'emergency_contact_name': 'Susan Wilson',
        'emergency_contact_phone': '555-1006', 'assigned_doctor': dr_smith, 'status': 'critical'
    })
    
    return patient1, patient2, patient3

def create_vitals(patients, nurse):
    print("Creating vital signs...")
    for patient in patients:
        for i in range(5):
            vital = VitalSign.objects.create(
                patient=patient, recorded_by=nurse,
                heart_rate=70 + i * 5, systolic_bp=120 + i * 3, diastolic_bp=80 + i * 2,
                temperature=Decimal('98.6'), spo2=98 - i, glucose=100 + i * 10,
                respiration_rate=16 + i
            )
            abnormals = vital.check_abnormal()
            for param, value, normal in abnormals:
                VitalAlert.objects.create(
                    patient=patient, vital_sign=vital, parameter=param,
                    value=str(value), normal_range=normal, severity='medium',
                    message=f"Abnormal {param}: {value} (Normal: {normal})"
                )

def create_medications(patients, doctor):
    print("Creating medications...")
    meds = [
        ('Aspirin', '100mg', 'once', 'Oral'),
        ('Metformin', '500mg', 'twice', 'Oral'),
        ('Lisinopril', '10mg', 'once', 'Oral'),
    ]
    for patient in patients:
        for name, dosage, freq, route in meds:
            Medication.objects.get_or_create(
                patient=patient, medicine_name=name, defaults={
                    'prescribed_by': doctor, 'dosage': dosage, 'frequency': freq,
                    'route': route, 'start_date': date.today(),
                    'end_date': date.today() + timedelta(days=30), 'status': 'active'
                }
            )

def create_appointments(patients, doctors):
    print("Creating appointments...")
    for i, patient in enumerate(patients):
        doctor = doctors[i % len(doctors)]
        Appointment.objects.get_or_create(
            patient=patient, doctor=doctor, appointment_date=date.today() + timedelta(days=i+1),
            defaults={
                'appointment_time': '10:00', 'appointment_type': 'consultation',
                'reason': 'Regular checkup', 'status': 'pending'
            }
        )
        Appointment.objects.get_or_create(
            patient=patient, doctor=doctor, appointment_date=date.today() + timedelta(days=i+7),
            defaults={
                'appointment_time': '14:00', 'appointment_type': 'followup',
                'reason': 'Follow-up visit', 'status': 'approved'
            }
        )

def create_notifications(users):
    print("Creating notifications...")
    for user in users:
        Notification.objects.get_or_create(
            user=user, title='Welcome to Healthcare Portal',
            defaults={'message': 'Your account has been set up successfully.', 'notification_type': 'info'}
        )

def main():
    print("Setting up Healthcare Portal sample data...")
    dr_smith, dr_jones, patient_user1 = create_users()
    patients = create_patients(dr_smith, dr_jones, patient_user1)
    
    nurse = User.objects.get(username='nurse_mary')
    create_vitals(patients, nurse)
    create_medications(patients, dr_smith)
    create_appointments(patients, [dr_smith, dr_jones])
    create_notifications([dr_smith, dr_jones, nurse, patient_user1])
    
    print("\n" + "="*50)
    print("Sample data created successfully!")
    print("="*50)
    print("\nLogin Credentials:")
    print("-" * 30)
    print("Admin:        admin / admin123")
    print("Doctor:       dr_smith / doctor123")
    print("Doctor:       dr_jones / doctor123")
    print("Nurse:        nurse_mary / nurse123")
    print("Receptionist: reception / reception123")
    print("Patient:      patient1 / patient123")
    print("="*50)

if __name__ == '__main__':
    main()
