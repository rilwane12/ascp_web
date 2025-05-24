from django.db import models
from django.utils import timezone
import os
import uuid
from django.conf import settings

class Medicament(models.Model):
    """Modèle pour stocker le catalogue de médicaments disponibles"""
    nom = models.CharField(max_length=255)
    forme = models.CharField(max_length=100, blank=True, null=True)
    dosage = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    prix = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="Prix")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Médicament"
        verbose_name_plural = "Médicaments"
        ordering = ['nom']
        
    def __str__(self):
        return self.nom

def prescription_image_path(instance, filename):
    """Génère un chemin unique pour les images de prescription"""
    ext = filename.split('.')[-1]
    patient_name = instance.consultation.patient.nom
    patient_surname = instance.consultation.patient.prenom
    date = timezone.now().strftime('%Y_%m_%d_%H_%M_%S')
    filename = f"{patient_name}_{patient_surname}_{date}.{ext}"
    return os.path.join('ordonnances_hist', filename)

class Ordonnance(models.Model):
    """Modèle pour les ordonnances médicales"""
    consultation = models.OneToOneField('examinations.Consultation', on_delete=models.CASCADE, related_name='ordonnance')
    date_prescription = models.DateTimeField(default=timezone.now)
    image = models.ImageField(upload_to=prescription_image_path, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Ordonnance"
        verbose_name_plural = "Ordonnances"
        ordering = ['-date_prescription']
        
    def __str__(self):
        return f"Ordonnance {self.id} - {self.consultation.patient} - {self.date_prescription.strftime('%d/%m/%Y')}"

class LignePrescription(models.Model):
    """Modèle pour les lignes individuelles de prescription dans une ordonnance"""
    ordonnance = models.ForeignKey(Ordonnance, on_delete=models.CASCADE, related_name='prescriptions')
    medicament = models.CharField(max_length=255)
    quantite = models.CharField(max_length=100, blank=True, null=True)
    posologie = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Ligne de prescription"
        verbose_name_plural = "Lignes de prescription"
        
    def __str__(self):
        return f"{self.medicament} - {self.quantite}"