from django import forms
from .models import Consultation, ExamenClinique, ExamenParaclinique
from patients.models import Patient

class ConsultationForm(forms.ModelForm):
    """Formulaire pour les consultations"""
    patient = forms.ModelChoiceField(
        queryset=Patient.objects.all().order_by('nom', 'prenom'),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Patient"
    )
    
    class Meta:
        model = Consultation
        fields = ['patient']
        widgets = {
            'patient': forms.Select(attrs={'class': 'form-select'}),
        }

class ExamenCliniqueForm(forms.ModelForm):
    """Formulaire pour les examens cliniques"""
    class Meta:
        model = ExamenClinique
        exclude = ['consultation', 'created_at', 'updated_at']
        widgets = {
            'poids': forms.TextInput(attrs={'class': 'form-control'}),
            'taille': forms.TextInput(attrs={'class': 'form-control'}),
            'temperature': forms.TextInput(attrs={'class': 'form-control'}),
            'fr_cardiaque': forms.TextInput(attrs={'class': 'form-control'}),
            'fr_respiratoire': forms.TextInput(attrs={'class': 'form-control'}),
            'sa_o2': forms.TextInput(attrs={'class': 'form-control'}),
            'conj_muq': forms.TextInput(attrs={'class': 'form-control'}),
            'atcd_med': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'atcd_chir': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'atcd_fam': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'mode_vie': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'plaintes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'examen_physique': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'examen_physique_1': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'examen_physique_2': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'examen_physique_3': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'hypothese_diagnostics': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'diagnostics': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'note_medecin': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class ExamenParacliniqueForm(forms.ModelForm):
    """Formulaire pour les examens paracliniques"""
    class Meta:
        model = ExamenParaclinique
        exclude = ['consultation', 'created_at', 'updated_at']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'resultat': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'date_demande': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'date_resultat': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local', 'required': False}),
        }