from django import forms
from .models import Patient

class PatientForm(forms.ModelForm):
    """Formulaire pour la création et modification de patients"""
    class Meta:
        model = Patient
        fields = ['nom', 'prenom', 'age', 'genre', 'profession', 'adresse', 
                  'contact', 'groupe_sanguin', 'allergies', 'n_donneur_sang']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'prenom': forms.TextInput(attrs={'class': 'form-control'}),
            'age': forms.TextInput(attrs={'class': 'form-control'}),
            'genre': forms.Select(attrs={'class': 'form-select'}),
            'profession': forms.TextInput(attrs={'class': 'form-control'}),
            'adresse': forms.TextInput(attrs={'class': 'form-control'}),
            'contact': forms.TextInput(attrs={'class': 'form-control'}),
            'groupe_sanguin': forms.Select(attrs={'class': 'form-select'}),
            'allergies': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'n_donneur_sang': forms.TextInput(attrs={'class': 'form-control'}),
        }