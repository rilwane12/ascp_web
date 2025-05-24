from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager
import os
from django.utils import timezone

class DoctorManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)

def doctor_profile_path(instance, filename):
    """Génère un chemin unique pour les photos de profil des médecins"""
    ext = filename.split('.')[-1]
    date = timezone.now().strftime('%Y%m%d%H%M%S')
    new_filename = f"dr_{instance.nom}_{instance.prenom}_{date}.{ext}"
    return os.path.join('doctor_profiles', new_filename)

class Doctor(AbstractUser):
    username = None
    email = models.EmailField(unique=True)
    n_ordre = models.CharField(max_length=100, unique=True, verbose_name="Numéro d'ordre")
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    specialite = models.CharField(max_length=100, blank=True, null=True)
    contact = models.CharField(max_length=20, blank=True, null=True)
    photo_profil = models.ImageField(upload_to=doctor_profile_path, blank=True, null=True, verbose_name="Photo de profil")
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['n_ordre', 'nom', 'prenom']
    
    objects = DoctorManager()
    
    class Meta:
        verbose_name = "Docteur"
        verbose_name_plural = "Docteurs"
    
    def __str__(self):
        return f"Dr. {self.nom} {self.prenom}"
    
    def full_name(self):
        return f"Dr. {self.nom} {self.prenom}"