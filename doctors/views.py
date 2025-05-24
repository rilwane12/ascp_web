from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import DoctorRegistrationForm, DoctorLoginForm, DoctorProfileForm
from .models import Doctor
from patients.models import Patient
from examinations.models import Consultation

def login_view(request):
    """Vue de connexion pour les médecins"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = DoctorLoginForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Bienvenue, Dr. {user.nom} {user.prenom}")
                return redirect('dashboard')
            else:
                messages.error(request, "Identifiants invalides")
    else:
        form = DoctorLoginForm(request)
    
    return render(request, 'doctors/login.html', {'form': form})

def register_view(request):
    """Vue d'inscription pour les médecins"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = DoctorRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Compte créé avec succès ! Bienvenue, Dr. {user.nom} {user.prenom}")
            return redirect('dashboard')
    else:
        form = DoctorRegistrationForm()
    
    return render(request, 'doctors/register.html', {'form': form})

@login_required
def dashboard(request):
    """Vue du tableau de bord principal"""
    # Récupérer les 5 derniers patients
    recent_patients = Patient.objects.all().order_by('-created_at')[:5]
    
    # Récupérer les 5 dernières consultations
    recent_consultations = Consultation.objects.filter(doctor=request.user).order_by('-date')[:5]
    
    return render(request, 'doctors/dashboard.html', {
        'recent_patients': recent_patients,
        'recent_consultations': recent_consultations
    })

@login_required
def profile(request):
    """Vue du profil du médecin"""
    return render(request, 'doctors/profile.html')

@login_required
def edit_profile(request):
    """Vue d'édition du profil du médecin"""
    if request.method == 'POST':
        form = DoctorProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profil mis à jour avec succès")
            return redirect('profile')
    else:
        form = DoctorProfileForm(instance=request.user)
    
    return render(request, 'doctors/edit_profile.html', {'form': form})

def logout_view(request):
    """Vue de déconnexion personnalisée"""
    logout(request)
    messages.success(request, "Vous avez été déconnecté avec succès")
    return redirect('login')
