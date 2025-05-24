from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Doctor

class DoctorRegistrationForm(UserCreationForm):
    """Formulaire d'inscription pour les médecins"""
    class Meta:
        model = Doctor
        fields = ('email', 'n_ordre', 'nom', 'prenom', 'specialite', 'contact')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Email'})
        self.fields['n_ordre'].widget.attrs.update({'class': 'form-control', 'placeholder': "Numéro d'ordre"})
        self.fields['nom'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Nom'})
        self.fields['prenom'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Prénom'})
        self.fields['specialite'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Spécialité'})
        self.fields['contact'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Contact'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Mot de passe'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirmation du mot de passe'})

class DoctorLoginForm(AuthenticationForm):
    """Formulaire de connexion pour les médecins"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Email'})
        self.fields['password'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Mot de passe'})

class DoctorProfileForm(forms.ModelForm):
    """Formulaire d'édition du profil médecin"""
    class Meta:
        model = Doctor
        fields = ('email', 'nom', 'prenom', 'specialite', 'contact', 'photo_profil')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update({'class': 'form-control'})
        self.fields['nom'].widget.attrs.update({'class': 'form-control'})
        self.fields['prenom'].widget.attrs.update({'class': 'form-control'})
        self.fields['specialite'].widget.attrs.update({'class': 'form-control'})
        self.fields['contact'].widget.attrs.update({'class': 'form-control'})
        self.fields['photo_profil'].widget.attrs.update({
            'class': 'form-control',
            'accept': 'image/*'
        })
