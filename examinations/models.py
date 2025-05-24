from django.db import models
from django.utils import timezone

class Consultation(models.Model):
    patient = models.ForeignKey('patients.Patient', on_delete=models.CASCADE, related_name='consultations')
    doctor = models.ForeignKey('doctors.Doctor', on_delete=models.CASCADE, related_name='consultations')
    date = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Consultation"
        verbose_name_plural = "Consultations"
        ordering = ['-date']
    
    def __str__(self):
        return f"Consultation {self.id} - {self.patient} - {self.date.strftime('%d/%m/%Y')}"

class ExamenClinique(models.Model):
    consultation = models.OneToOneField(Consultation, on_delete=models.CASCADE, related_name='examen_clinique')
    
    # Constantes vitales
    poids = models.CharField(max_length=10, blank=True, null=True)
    taille = models.CharField(max_length=10, blank=True, null=True)
    temperature = models.CharField(max_length=10, blank=True, null=True)
    fr_cardiaque = models.CharField(max_length=10, blank=True, null=True, verbose_name="Fréquence cardiaque")
    fr_respiratoire = models.CharField(max_length=10, blank=True, null=True, verbose_name="Fréquence respiratoire")
    sa_o2 = models.CharField(max_length=10, blank=True, null=True, verbose_name="Saturation en oxygène")
    conj_muq = models.CharField(max_length=100, blank=True, null=True, verbose_name="Conjonctives et muqueuses")
    
    # Antécédents et plaintes
    atcd_med = models.TextField(blank=True, null=True, verbose_name="Antécédents médicaux")
    atcd_chir = models.TextField(blank=True, null=True, verbose_name="Antécédents chirurgicaux")
    atcd_fam = models.TextField(blank=True, null=True, verbose_name="Antécédents familiaux")
    mode_vie = models.TextField(blank=True, null=True, verbose_name="Mode de vie")
    plaintes = models.TextField(blank=True, null=True)
    
    # Examens physiques et diagnostics
    examen_physique = models.TextField(blank=True, null=True)
    examen_physique_1 = models.TextField(blank=True, null=True)
    examen_physique_2 = models.TextField(blank=True, null=True)
    examen_physique_3 = models.TextField(blank=True, null=True)
    hypothese_diagnostics = models.TextField(blank=True, null=True, verbose_name="Hypothèses diagnostiques")
    diagnostics = models.TextField(blank=True, null=True)
    note_medecin = models.TextField(blank=True, null=True, verbose_name="Note du médecin")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Examen clinique"
        verbose_name_plural = "Examens cliniques"
    
    def __str__(self):
        return f"Examen clinique - {self.consultation}"

class ExamenParaclinique(models.Model):
    consultation = models.ForeignKey(Consultation, on_delete=models.CASCADE, related_name='examens_paracliniques')
    nom = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    resultat = models.TextField(blank=True, null=True)
    date_demande = models.DateTimeField(default=timezone.now)
    date_resultat = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Examen paraclinique"
        verbose_name_plural = "Examens paracliniques"
        ordering = ['-date_demande']
    
    def __str__(self):
        return f"{self.nom} - {self.consultation.patient}"