from django.urls import path
from . import views

app_name = 'vitals'

urlpatterns = [
    path('', views.vitals_list, name='vitals_list'),
    path('patient/<int:patient_id>/', views.patient_vitals, name='patient_vitals'),
    path('patient/<int:patient_id>/add/', views.add_vital, name='add_vital'),
    path('patient/<int:patient_id>/chart/', views.vitals_chart, name='vitals_chart'),
    path('patient/<int:patient_id>/chart-data/', views.vitals_chart_data, name='vitals_chart_data'),
    path('alerts/', views.alerts_list, name='alerts_list'),
    path('alerts/<int:pk>/resolve/', views.resolve_alert, name='resolve_alert'),
]
