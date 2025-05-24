from django.urls import path
from . import views

urlpatterns = [
    path('', views.consultation_list, name='consultation_list'),
    path('create/', views.consultation_create, name='consultation_create'),
    path('<int:pk>/', views.consultation_detail, name='consultation_detail'),
    path('<int:pk>/clinical/', views.clinical_exam_create, name='clinical_exam_create'),
    path('<int:pk>/clinical/edit/', views.clinical_exam_edit, name='clinical_exam_edit'),
    path('<int:pk>/paraclinical/', views.paraclinical_exam_create, name='paraclinical_exam_create'),
    path('<int:pk>/paraclinical/<int:exam_pk>/edit/', views.paraclinical_exam_edit, name='paraclinical_exam_edit'),
    path('<int:pk>/paraclinical/<int:exam_pk>/delete/', views.paraclinical_exam_delete, name='paraclinical_exam_delete'),
]