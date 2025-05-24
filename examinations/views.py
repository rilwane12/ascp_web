from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from .models import Consultation, ExamenClinique, ExamenParaclinique
from .forms import ConsultationForm, ExamenCliniqueForm, ExamenParacliniqueForm
from patients.models import Patient

@login_required
def consultation_list(request):
    """Liste des consultations"""
    consultations = Consultation.objects.filter(doctor=request.user).order_by('-date')
    return render(request, 'examinations/consultation_list.html', {'consultations': consultations})

@login_required
def consultation_create(request):
    """Création d'une nouvelle consultation"""
    if request.method == 'POST':
        form = ConsultationForm(request.POST)
        if form.is_valid():
            consultation = form.save(commit=False)
            consultation.doctor = request.user
            consultation.date = timezone.now()
            consultation.save()
            return redirect('consultation_detail', pk=consultation.pk)
    else:
        # Vérifie si un patient a été spécifié dans l'URL
        patient_id = request.GET.get('patient')
        if patient_id:
            try:
                patient = Patient.objects.get(id=patient_id)
                # Initialise le formulaire avec ce patient
                form = ConsultationForm(initial={'patient': patient})
            except Patient.DoesNotExist:
                form = ConsultationForm()
        else:
            form = ConsultationForm()
    
    return render(request, 'examinations/consultation_form.html', {'form': form})

@login_required
def consultation_detail(request, pk):
    """Détail d'une consultation avec ses examens"""
    consultation = get_object_or_404(Consultation, pk=pk, doctor=request.user)
    
    try:
        examen_clinique = consultation.examen_clinique
    except ExamenClinique.DoesNotExist:
        examen_clinique = None
    
    examens_paracliniques = consultation.examens_paracliniques.all()
    
    return render(request, 'examinations/consultation_detail.html', {
        'consultation': consultation,
        'examen_clinique': examen_clinique,
        'examens_paracliniques': examens_paracliniques
    })

@login_required
def clinical_exam_create(request, pk):
    """Création d'un examen clinique pour une consultation"""
    consultation = get_object_or_404(Consultation, pk=pk, doctor=request.user)
    
    try:
        # Vérifie si un examen clinique existe déjà
        examen_clinique = consultation.examen_clinique
        return redirect('clinical_exam_edit', pk=pk)
    except ExamenClinique.DoesNotExist:
        pass
    
    if request.method == 'POST':
        form = ExamenCliniqueForm(request.POST)
        if form.is_valid():
            examen_clinique = form.save(commit=False)
            examen_clinique.consultation = consultation
            examen_clinique.save()
            return redirect('consultation_detail', pk=pk)
    else:
        form = ExamenCliniqueForm()
    
    return render(request, 'examinations/clinical_exam_form.html', {
        'form': form,
        'consultation': consultation
    })

@login_required
def clinical_exam_edit(request, pk):
    """Modification d'un examen clinique existant"""
    consultation = get_object_or_404(Consultation, pk=pk, doctor=request.user)
    
    try:
        examen_clinique = consultation.examen_clinique
    except ExamenClinique.DoesNotExist:
        return redirect('clinical_exam_create', pk=pk)
    
    if request.method == 'POST':
        form = ExamenCliniqueForm(request.POST, instance=examen_clinique)
        if form.is_valid():
            form.save()
            return redirect('consultation_detail', pk=pk)
    else:
        form = ExamenCliniqueForm(instance=examen_clinique)
    
    return render(request, 'examinations/clinical_exam_form.html', {
        'form': form,
        'consultation': consultation,
        'examen_clinique': examen_clinique
    })

@login_required
def paraclinical_exam_create(request, pk):
    """Ajout d'un examen paraclinique à une consultation"""
    consultation = get_object_or_404(Consultation, pk=pk, doctor=request.user)
    
    if request.method == 'POST':
        form = ExamenParacliniqueForm(request.POST)
        if form.is_valid():
            examen = form.save(commit=False)
            examen.consultation = consultation
            examen.save()
            return redirect('consultation_detail', pk=pk)
    else:
        form = ExamenParacliniqueForm()
    
    return render(request, 'examinations/paraclinical_exam_form.html', {
        'form': form,
        'consultation': consultation
    })

@login_required
def paraclinical_exam_edit(request, pk, exam_pk):
    """Modification d'un examen paraclinique"""
    consultation = get_object_or_404(Consultation, pk=pk, doctor=request.user)
    examen = get_object_or_404(ExamenParaclinique, pk=exam_pk, consultation=consultation)
    
    if request.method == 'POST':
        form = ExamenParacliniqueForm(request.POST, instance=examen)
        if form.is_valid():
            form.save()
            return redirect('consultation_detail', pk=pk)
    else:
        form = ExamenParacliniqueForm(instance=examen)
    
    return render(request, 'examinations/paraclinical_exam_form.html', {
        'form': form,
        'consultation': consultation,
        'examen': examen
    })

@login_required
def paraclinical_exam_delete(request, pk, exam_pk):
    """Suppression d'un examen paraclinique"""
    consultation = get_object_or_404(Consultation, pk=pk, doctor=request.user)
    examen = get_object_or_404(ExamenParaclinique, pk=exam_pk, consultation=consultation)
    
    if request.method == 'POST':
        examen.delete()
        return redirect('consultation_detail', pk=pk)
    
    return render(request, 'examinations/paraclinical_exam_confirm_delete.html', {
        'examen': examen,
        'consultation': consultation
    })