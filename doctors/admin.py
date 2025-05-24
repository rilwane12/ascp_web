from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Doctor
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html

@admin.register(Doctor)
class DoctorAdmin(UserAdmin):
    list_display = ('full_name_display', 'email', 'n_ordre', 'specialite', 'contact', 'is_active', 'is_staff', 'date_joined')
    list_filter = ('specialite', 'is_active', 'is_staff', 'is_superuser', 'date_joined')
    search_fields = ('nom', 'prenom', 'email', 'n_ordre', 'specialite')
    ordering = ('nom', 'prenom', 'date_joined')
    
    # Actions personnalisées
    actions = ['mark_as_active', 'mark_as_inactive']
    
    def mark_as_active(self, request, queryset):
        queryset.update(is_active=True)
    mark_as_active.short_description = "Marquer les médecins sélectionnés comme actifs"
    
    def mark_as_inactive(self, request, queryset):
        queryset.update(is_active=False)
    mark_as_inactive.short_description = "Marquer les médecins sélectionnés comme inactifs"
    
    def full_name_display(self, obj):
        if obj.photo_profil:
            return format_html('<img src="{}" width="30" height="30" style="border-radius: 50%; margin-right: 10px;" /> {}', obj.photo_profil.url, obj.full_name())
        return obj.full_name()
    full_name_display.short_description = "Médecin"
    
    # Personnalisation des formulaires
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Informations personnelles'), {'fields': ('nom', 'prenom', 'specialite', 'n_ordre', 'contact', 'photo_profil')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Dates importantes'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'nom', 'prenom', 'n_ordre', 'specialite', 'contact'),
        }),
    )
    readonly_fields = ['date_joined', 'last_login']
