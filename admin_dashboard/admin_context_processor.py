"""
Context processor pour l'administration Asclepios.
Rend les statistiques et autres données disponibles dans tous les templates d'administration.
"""

from doctors.models import Doctor
from patients.models import Patient
from examinations.models import Consultation
from prescriptions.models import Ordonnance
from django.urls import reverse


def admin_stats(request):
    """
    Context processor qui fournit des statistiques et d'autres données utiles
    à tous les templates d'administration.
    """
    # Vérifier si nous sommes dans l'administration
    is_admin = request.path.startswith('/admin/')
    
    # Par défaut, retourner un dictionnaire vide ou avec juste l'URL du tableau de bord
    context = {
        'dashboard_url': reverse('admin_dashboard:dashboard') if is_admin else None,
        'is_admin_section': is_admin,
    }
    
    # Si nous sommes dans l'administration, ajouter les statistiques
    if is_admin:
        try:
            stats = {
                'patients_count': Patient.objects.count(),
                'doctors_count': Doctor.objects.filter(is_active=True).count(),
                'consultations_count': Consultation.objects.count(),
                'prescriptions_count': Ordonnance.objects.count(),
            }
            context.update(stats)
            
            # Récentes activités (si nécessaire pour les templates)
            # Vous pouvez ajuster ces requêtes selon vos besoins réels
            context.update({
                'recent_patients': Patient.objects.order_by('-created_at')[:5],
                'recent_consultations': Consultation.objects.order_by('-date')[:5],
                'recent_prescriptions': Ordonnance.objects.order_by('-date_prescription')[:5],
            })
            
        except Exception as e:
            # En cas d'erreur (par exemple si les tables n'existent pas encore)
            context.update({
                'patients_count': 0,
                'doctors_count': 0,
                'consultations_count': 0,
                'prescriptions_count': 0,
                'recent_patients': [],
                'recent_consultations': [],
                'recent_prescriptions': [],
            })
    
    return context

