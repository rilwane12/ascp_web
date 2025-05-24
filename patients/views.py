from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib import messages

from .models import Patient
from .forms import PatientForm
from examinations.models import Consultation

@login_required
def patient_list(request):
    """Liste des patients avec recherche et filtrage"""
    # Récupérer tous les patients
    patients = Patient.objects.all().order_by('-created_at')
    
    # Recherche
    search_query = request.GET.get('search', '')
    if search_query:
        patients = patients.filter(
            Q(nom__icontains=search_query) | 
            Q(prenom__icontains=search_query) |
            Q(contact__icontains=search_query)
        )
    
    # Filtrage par genre
    genre = request.GET.get('genre', '')
    if genre:
        patients = patients.filter(genre=genre)
    
    # Filtrage par groupe sanguin
    groupe_sanguin = request.GET.get('groupe_sanguin', '')
    if groupe_sanguin:
        patients = patients.filter(groupe_sanguin=groupe_sanguin)
    
    # Pagination
    paginator = Paginator(patients, 10)  # 10 patients par page
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # Contexte pour le template
    context = {
        'patients': page_obj,
        'search_query': search_query,
        'blood_groups': Patient.BLOOD_GROUP_CHOICES,
    }
    
    return render(request, 'patients/patient_list.html', context)

@login_required
def patient_create(request):
    """Création d'un nouveau patient"""
    if request.method == 'POST':
        form = PatientForm(request.POST)
        if form.is_valid():
            patient = form.save()
            messages.success(request, f"Le patient {patient.nom} {patient.prenom} a été créé avec succès.")
            if 'save_and_add_consultation' in request.POST:
                return redirect(f"{reverse('consultation_create')}?patient={patient.id}")
            return redirect('patient_detail', pk=patient.pk)
    else:
        form = PatientForm()
    
    return render(request, 'patients/patient_form.html', {
        'form': form,
        'action': 'create'
    })

@login_required
def patient_detail(request, pk):
    """Détails d'un patient et son historique médical"""
    patient = get_object_or_404(Patient, pk=pk)
    consultations = Consultation.objects.filter(patient=patient).order_by('-date')
    
    return render(request, 'patients/patient_detail.html', {
        'patient': patient,
        'consultations': consultations
    })

@login_required
def patient_edit(request, pk):
    """Modification des informations d'un patient"""
    patient = get_object_or_404(Patient, pk=pk)
    
    if request.method == 'POST':
        form = PatientForm(request.POST, instance=patient)
        if form.is_valid():
            patient = form.save()
            messages.success(request, f"Les informations de {patient.nom} {patient.prenom} ont été mises à jour.")
            return redirect('patient_detail', pk=patient.pk)
    else:
        form = PatientForm(instance=patient)
    
    return render(request, 'patients/patient_form.html', {
        'form': form,
        'patient': patient,
        'action': 'edit'
    })