from django.contrib import admin
from django.urls import path, reverse
from django.utils.html import format_html
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.decorators import user_passes_test
from django.conf import settings
from functools import update_wrapper

# Imports pour les statistiques
from doctors.models import Doctor
from patients.models import Patient
from examinations.models import Consultation
from prescriptions.models import Ordonnance

# Importer notre vue personnalisée
from .views import custom_admin_index

# Personnaliser l'interface d'administration Django
admin.site.site_header = "Administration Asclepios"
admin.site.site_title = "Asclepios Admin"
admin.site.index_title = "Tableau de bord d'administration"

# Remplacer la vue d'index par défaut par notre vue personnalisée
admin.site.index = custom_admin_index

# Classe de base pour l'authentification à deux facteurs
class TwoFactorAdminSite(admin.AdminSite):
    """
    Une version personnalisée du site d'administration avec authentification à deux facteurs.
    Cette classe est préparée pour l'implémentation future de l'authentification 2FA.
    """
    login_template = 'admin_dashboard/admin_login.html'
    
    def has_permission(self, request):
        """Vérifie si l'utilisateur a les permissions et a passé l'authentification 2FA"""
        # Pour l'instant, nous utilisons simplement la logique standard
        # Dans l'implémentation complète, vérifiez également si l'authentification 2FA est validée
        return super().has_permission(request)

# Middleware pour l'authentification à deux facteurs (à développer ultérieurement)
class TwoFactorAuthMiddleware:
    """Middleware pour gérer l'authentification à deux facteurs pour les administrateurs"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # Ici, on pourrait vérifier si l'utilisateur est authentifié, est un admin,
        # et a passé l'authentification 2FA
        # Si l'authentification 2FA n'est pas validée et que l'utilisateur accède à l'admin,
        # rediriger vers la page 2FA
        
        response = self.get_response(request)
        return response

# Modèle pour stocker les informations d'authentification à deux facteurs (à implémenter ultérieurement)
# from django.db import models
# class TwoFactorAuth(models.Model):
#     user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#     secret_key = models.CharField(max_length=100)
#     is_enabled = models.BooleanField(default=False)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

# Mixin pour les actions en masse sur les modèles d'administration
class ExportMixin:
    """Mixin pour ajouter des fonctionnalités d'exportation aux modèles d'administration"""
    
    actions = ['export_as_csv']
    
    def export_as_csv(self, request, queryset):
        """Exporter les objets sélectionnés en CSV"""
        import csv
        from django.http import HttpResponse
        
        meta = self.model._meta
        field_names = [field.name for field in meta.fields]
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename={meta.verbose_name_plural}-export.csv'
        writer = csv.writer(response)
        
        writer.writerow(field_names)
        for obj in queryset:
            writer.writerow([getattr(obj, field) for field in field_names])
            
        return response
    export_as_csv.short_description = "Exporter les éléments sélectionnés en CSV"

# Décorateur pour vérifier si l'utilisateur est un superutilisateur
def superuser_required(view_func):
    """Décorateur qui vérifie si l'utilisateur est un superutilisateur"""
    decorated_view = user_passes_test(lambda u: u.is_superuser)(view_func)
    return decorated_view

# Vue personnalisée pour l'administration Django
class CustomAdminView(admin.ModelAdmin):
    """Classe de base pour les vues d'administration personnalisées"""
    
    change_list_template = 'admin_dashboard/admin_change_list.html'
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('dashboard/', self.admin_site.admin_view(self.dashboard_view), name='admin_dashboard'),
        ]
        return custom_urls + urls
    
    def dashboard_view(self, request):
        """Vue pour rediriger vers le tableau de bord personnalisé"""
        return HttpResponseRedirect(reverse('admin_dashboard:dashboard'))

# Ajouter un bouton vers le tableau de bord dans l'administration
def add_dashboard_button(request, extra_context=None):
    """Fonction pour ajouter un bouton vers le tableau de bord dans l'administration"""
    extra_context = extra_context or {}
    extra_context['dashboard_url'] = reverse('admin_dashboard:dashboard')
    return extra_context

# Fonction pour récupérer les statistiques pour l'administration
def get_admin_stats():
    """Récupérer les statistiques globales pour l'administration"""
    try:
        stats = {
            'patients_count': Patient.objects.count(),
            'doctors_count': Doctor.objects.filter(is_active=True).count(),
            'consultations_count': Consultation.objects.count(),
            'prescriptions_count': Ordonnance.objects.count(),
        }
    except Exception as e:
        # En cas d'erreur (par exemple, si les tables n'existent pas encore)
        stats = {
            'patients_count': 0,
            'doctors_count': 0,
            'consultations_count': 0,
            'prescriptions_count': 0,
        }
    return stats

# Personnaliser l'en-tête d'administration pour ajouter un lien vers le tableau de bord
def get_each_context(request):
    """
    Fonction pour personnaliser le contexte de l'administration.
    Inclut le lien vers le tableau de bord et les statistiques.
    """
    context = {
        'site_header': admin.site.site_header,
        'site_title': admin.site.site_title,
        'index_title': admin.site.index_title,
        'has_permission': admin.site.has_permission(request),
        'dashboard_url': reverse('admin_dashboard:dashboard'),
    }
    
    # Ajouter les statistiques au contexte (seulement pour la page d'index)
    if request.path == '/admin/' or request.path == '/admin':
        context.update(get_admin_stats())
    
    return context

# Remplacer la fonction each_context par notre fonction personnalisée
admin.site.each_context = get_each_context

# Usage: Pour ajouter le mixin d'exportation à un modèle d'administration
# @admin.register(YourModel)
# class YourModelAdmin(ExportMixin, admin.ModelAdmin):
#     list_display = ('field1', 'field2')
#     ...
