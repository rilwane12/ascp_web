from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Q
from django.db.models.functions import TruncDay, TruncMonth
from django.utils import timezone
from datetime import timedelta
from django.urls import reverse

from doctors.models import Doctor
from patients.models import Patient
from examinations.models import Consultation, ExamenClinique, ExamenParaclinique
from prescriptions.models import Ordonnance, Medicament

def get_admin_stats():
    """
    Récupère les statistiques générales pour l'administration
    """
    try:
        stats = {
            'patients_count': Patient.objects.count(),
            'doctors_count': Doctor.objects.filter(is_active=True).count(),
            'consultations_count': Consultation.objects.count(),
            'prescriptions_count': Ordonnance.objects.count(),
            'medicaments_count': Medicament.objects.count(),
            
            # Ajouter d'autres statistiques si nécessaire
            'recent_activity': True,  # Indicateur pour l'interface
        }
    except Exception as e:
        # En cas d'erreur (par exemple, si les tables n'existent pas encore)
        stats = {
            'patients_count': 0,
            'doctors_count': 0,
            'consultations_count': 0,
            'prescriptions_count': 0,
            'medicaments_count': 0,
            'recent_activity': False,
        }
    return stats

@staff_member_required
def admin_dashboard(request):
    """
    Vue principale du tableau de bord d'administration
    Affiche des statistiques générales et des graphiques sur l'activité
    """
    # Statistiques globales
    stats = {
        'total_patients': Patient.objects.count(),
        'total_doctors': Doctor.objects.filter(is_active=True).count(),
        'total_consultations': Consultation.objects.count(),
        'total_ordonnances': Ordonnance.objects.count(),
        'total_medicaments': Medicament.objects.count(),
    }
    
    # Statistiques des patients par genre
    patients_by_gender = Patient.objects.values('genre').annotate(count=Count('id'))
    
    # Consultations récentes (30 derniers jours)
    today = timezone.now()
    last_month = today - timedelta(days=30)
    
    consultations_by_day = (
        Consultation.objects
        .filter(date__gte=last_month)
        .annotate(day=TruncDay('date'))
        .values('day')
        .annotate(count=Count('id'))
        .order_by('day')
    )
    
    # Consultations par médecin (top 5)
    consultations_by_doctor = (
        Consultation.objects
        .values('doctor__nom', 'doctor__prenom')
        .annotate(count=Count('id'))
        .order_by('-count')[:5]
    )
    
    # Dernières consultations
    recent_consultations = (
        Consultation.objects
        .select_related('patient', 'doctor')
        .order_by('-date')[:10]
    )
    
    # Derniers patients enregistrés
    recent_patients = (
        Patient.objects
        .order_by('-created_at')[:10]
    )
    
    # Dernières ordonnances
    recent_ordonnances = (
        Ordonnance.objects
        .select_related('consultation__patient', 'consultation__doctor')
        .order_by('-date_prescription')[:10]
    )
    
    # Préparer les données pour les graphiques
    chart_data = {
        'patients_by_gender': list(patients_by_gender),
        'consultations_by_day': list(consultations_by_day),
        'consultations_by_doctor': list(consultations_by_doctor),
    }
    
    context = {
        'stats': stats,
        'chart_data': chart_data,
        'recent_consultations': recent_consultations,
        'recent_patients': recent_patients,
        'recent_ordonnances': recent_ordonnances,
    }
    
    return render(request, 'admin_dashboard/dashboard.html', context)

@staff_member_required
def patient_analytics(request):
    """
    Vue détaillée des statistiques concernant les patients
    """
    # Distribution des âges
    patients_by_age = (
        Patient.objects
        .values('age')
        .annotate(count=Count('id'))
        .order_by('age')
    )
    
    # Croissance mensuelle des patients (12 derniers mois)
    today = timezone.now()
    last_year = today - timedelta(days=365)
    
    patients_by_month = (
        Patient.objects
        .filter(created_at__gte=last_year)
        .annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )
    
    context = {
        'patients_by_age': list(patients_by_age),
        'patients_by_month': list(patients_by_month),
        'total_patients': Patient.objects.count(),
        'patients_gender_ratio': {
            'M': Patient.objects.filter(genre='M').count(),
            'F': Patient.objects.filter(genre='F').count(),
        }
    }
    
    return render(request, 'admin_dashboard/patient_analytics.html', context)

@staff_member_required
def consultation_analytics(request):
    """
    Vue détaillée des statistiques concernant les consultations
    """
    # Consultations par mois (12 derniers mois)
    today = timezone.now()
    last_year = today - timedelta(days=365)
    
    consultations_by_month = (
        Consultation.objects
        .filter(date__gte=last_year)
        .annotate(month=TruncMonth('date'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )
    
    # Consultations avec examen clinique vs sans examen clinique
    consultations_with_exam = Consultation.objects.filter(examen_clinique__isnull=False).count()
    consultations_without_exam = Consultation.objects.filter(examen_clinique__isnull=True).count()
    
    # Examens paracliniques par type
    examens_paracliniques = (
        ExamenParaclinique.objects
        .values('nom')
        .annotate(count=Count('id'))
        .order_by('-count')[:10]
    )
    
    context = {
        'consultations_by_month': list(consultations_by_month),
        'consultation_exam_stats': {
            'with_exam': consultations_with_exam,
            'without_exam': consultations_without_exam,
        },
        'examens_paracliniques': list(examens_paracliniques),
        'total_consultations': Consultation.objects.count(),
    }
    
    return render(request, 'admin_dashboard/consultation_analytics.html', context)

@staff_member_required
def prescription_analytics(request):
    """
    Vue détaillée des statistiques concernant les prescriptions
    """
    # Médicaments les plus prescrits
    top_medicaments = (
        Medicament.objects
        .values('nom')
        .annotate(count=Count('id'))
        .order_by('-count')[:10]
    )
    
    # Ordonnances par mois (12 derniers mois)
    today = timezone.now()
    last_year = today - timedelta(days=365)
    
    ordonnances_by_month = (
        Ordonnance.objects
        .filter(date_prescription__gte=last_year)
        .annotate(month=TruncMonth('date_prescription'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )
    
    context = {
        'top_medicaments': list(top_medicaments),
        'ordonnances_by_month': list(ordonnances_by_month),
        'total_ordonnances': Ordonnance.objects.count(),
        'total_medicaments': Medicament.objects.count(),
    }
    
    return render(request, 'admin_dashboard/prescription_analytics.html', context)

@staff_member_required
def system_logs(request):
    """
    Vue pour afficher les journaux d'activité du système
    Note: Nécessite une implémentation plus approfondie pour les logs réels
    """
    # Simuler les logs pour la démonstration
    # Dans une implémentation réelle, vous utiliseriez un système de journalisation
    system_logs = [
        {'timestamp': timezone.now() - timedelta(minutes=5), 'user': 'admin', 'action': 'Connexion', 'severity': 'info'},
        {'timestamp': timezone.now() - timedelta(minutes=10), 'user': 'admin', 'action': 'Modification patient #42', 'severity': 'info'},
        {'timestamp': timezone.now() - timedelta(hours=1), 'user': 'docteur1', 'action': 'Création d\'une consultation', 'severity': 'info'},
        {'timestamp': timezone.now() - timedelta(hours=2), 'user': 'système', 'action': 'Sauvegarde automatique', 'severity': 'success'},
        {'timestamp': timezone.now() - timedelta(hours=3), 'user': 'docteur2', 'action': 'Tentative de connexion échouée', 'severity': 'warning'},
    ]
    
    context = {
        'system_logs': system_logs
    }
    
    return render(request, 'admin_dashboard/system_logs.html', context)


@staff_member_required
def custom_admin_index(request, extra_context=None):
    """
    Vue personnalisée qui remplace la vue d'index par défaut de l'administration Django.
    Inclut les statistiques et d'autres informations utiles.
    """
    from django.contrib.admin.sites import site
    from django.contrib.admin.models import LogEntry
    
    # Récupérer le contexte standard de l'administration Django
    context = {
        **site.each_context(request),
        'title': 'Administration',
        'app_list': site.get_app_list(request),
        'log_entries': LogEntry.objects.select_related("content_type", "user"),
    }
    
    # Ajouter nos statistiques personnalisées
    stats = get_admin_stats()
    context.update(stats)
    
    # Ajouter des activités récentes
    try:
        # Récupérer les dernières consultations
        context['recent_consultations'] = Consultation.objects.select_related(
            'patient', 'doctor'
        ).order_by('-date')[:5]
        
        # Récupérer les derniers patients
        context['recent_patients'] = Patient.objects.order_by('-created_at')[:5]
        
        # Récupérer les dernières ordonnances
        context['recent_prescriptions'] = Ordonnance.objects.select_related(
            'consultation__patient', 'consultation__doctor'
        ).order_by('-date_prescription')[:5]
    except Exception as e:
        # En cas d'erreur, utiliser des listes vides
        context['recent_consultations'] = []
        context['recent_patients'] = []
        context['recent_prescriptions'] = []
    
    # Ajouter l'URL du tableau de bord
    context['dashboard_url'] = reverse('admin_dashboard:dashboard')
    
    # Ajouter le contexte supplémentaire si fourni
    if extra_context:
        context.update(extra_context)
    
    # Afficher le template standard de l'index d'administration
    return render(request, 'admin/index.html', context)
