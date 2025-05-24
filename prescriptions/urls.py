from django.urls import path
from . import views

urlpatterns = [
    path('', views.prescription_list, name='prescription_list'),
    path('create/<int:consultation_id>/', views.prescription_create, name='prescription_create'),
    path('<int:pk>/', views.prescription_detail, name='prescription_detail'),
    path('<int:pk>/edit/', views.prescription_edit, name='prescription_edit'),
    path('<int:pk>/pdf/', views.prescription_pdf, name='prescription_pdf'),
    path('ligne/<int:pk>/delete/', views.ligne_prescription_delete, name='ligne_prescription_delete'),
    path('medicaments/', views.medicament_list, name='medicament_list'),
    path('medicaments/create/', views.medicament_create, name='medicament_create'),
    path('medicaments/<int:pk>/edit/', views.medicament_edit, name='medicament_edit'),
]