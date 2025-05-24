from django.apps import AppConfig


class AdminDashboardConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'admin_dashboard'
    verbose_name = "Tableau de bord d'administration"
    
    def ready(self):
        """
        Cette méthode est appelée lorsque l'application est prête.
        Nous pouvons l'utiliser pour enregistrer des signaux ou effectuer d'autres tâches d'initialisation.
        """
        # Import ici pour éviter les problèmes d'importation circulaire
        # Commenté pour l'instant car le module n'existe pas encore
        # import admin_dashboard.signals
