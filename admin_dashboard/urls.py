from django.urls import path
from . import views

app_name = 'admin_dashboard'

urlpatterns = [
    path('', views.admin_dashboard, name='dashboard'),
    path('patients/', views.patient_analytics, name='patient_analytics'),
    path('consultations/', views.consultation_analytics, name='consultation_analytics'),
    path('prescriptions/', views.prescription_analytics, name='prescription_analytics'),
    path('logs/', views.system_logs, name='system_logs'),
]

