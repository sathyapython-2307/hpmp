from django.urls import path
from . import views

app_name = 'medications'

urlpatterns = [
    path('', views.medication_list, name='medication_list'),
    path('patient/<int:patient_id>/', views.patient_medications, name='patient_medications'),
    path('patient/<int:patient_id>/add/', views.add_medication, name='add_medication'),
    path('<int:pk>/edit/', views.edit_medication, name='edit_medication'),
    path('<int:pk>/delete/', views.delete_medication, name='delete_medication'),
    path('<int:pk>/mark-taken/', views.mark_taken, name='mark_taken'),
    path('treatments/', views.treatment_list, name='treatment_list'),
    path('treatments/patient/<int:patient_id>/add/', views.add_treatment, name='add_treatment'),
    path('treatments/<int:pk>/edit/', views.edit_treatment, name='edit_treatment'),
]
