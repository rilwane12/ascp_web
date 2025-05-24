from django import forms
from .models import Ordonnance, LignePrescription, Medicament

class OrdonnanceForm(forms.ModelForm):
    """Formulaire pour créer une ordonnance"""
    class Meta:
        model = Ordonnance
        fields = []  # Pas de champs supplémentaires nécessaires, tout est défini par la vue

class LignePrescriptionForm(forms.ModelForm):
    """Formulaire pour ajouter un médicament à une ordonnance"""
    class Meta:
        model = LignePrescription
        fields = ['medicament', 'quantite', 'posologie']
        widgets = {
            'medicament': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'medicament-autocomplete',
                'placeholder': 'Nom du médicament'
            }),
            'quantite': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: 1 boîte, 30 comprimés, etc.'
            }),
            'posologie': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: 1 comprimé matin, midi et soir pendant 5 jours',
                'rows': 3
            }),
        }

class MedicamentForm(forms.ModelForm):
    """Formulaire pour créer/modifier un médicament"""
    class Meta:
        model = Medicament
        fields = ['nom', 'forme', 'dosage', 'description', 'prix']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'forme': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: comprimé, gélule, sirop, etc.'
            }),
            'dosage': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: 500mg, 1g, 100ml, etc.'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Description du médicament (optionnelle)'
            }),
            'prix': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: 1345',
                'step': '1'
            }),
        }
