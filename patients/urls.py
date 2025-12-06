from django.urls import path
from . import views

app_name = 'patients'

urlpatterns = [
    path('', views.patient_list, name='patient_list'),
    path('add/', views.patient_add, name='patient_add'),
    path('<int:pk>/', views.patient_detail, name='patient_detail'),
    path('<int:pk>/edit/', views.patient_edit, name='patient_edit'),
    path('<int:pk>/delete/', views.patient_delete, name='patient_delete'),
    path('<int:pk>/history/add/', views.add_medical_history, name='add_medical_history'),
    path('<int:pk>/file/upload/', views.upload_medical_file, name='upload_medical_file'),
    path('file/<int:pk>/delete/', views.delete_medical_file, name='delete_medical_file'),
]
