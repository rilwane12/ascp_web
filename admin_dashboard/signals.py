"""
Signaux pour l'application admin_dashboard.
Ce fichier peut être utilisé pour définir des gestionnaires de signaux
pour suivre les actions d'administration, comme la connexion, la création/modification/suppression d'objets, etc.
"""

from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.dispatch import receiver

# Exemple de gestionnaire de signal pour la connexion d'un utilisateur
# @receiver(user_logged_in)
# def user_logged_in_handler(sender, request, user, **kwargs):
#     """
#     Gestionnaire pour le signal de connexion d'un utilisateur.
#     Pourrait être utilisé pour journaliser les connexions.
#     """
#     # LogEntry.objects.create(
#     #     user=user,
#     #     action='Connexion',
#     #     ip_address=get_client_ip(request),
#     #     user_agent=request.META.get('HTTP_USER_AGENT', ''),
#     # )

