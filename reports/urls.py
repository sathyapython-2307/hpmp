from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.report_list, name='report_list'),
    path('patient/<int:patient_id>/', views.patient_reports, name='patient_reports'),
    path('patient/<int:patient_id>/upload/', views.upload_report, name='upload_report'),
    path('<int:pk>/', views.report_detail, name='report_detail'),
    path('<int:pk>/edit/', views.edit_report, name='edit_report'),
    path('<int:pk>/delete/', views.delete_report, name='delete_report'),
]
