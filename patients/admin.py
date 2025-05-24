from django.contrib import admin
from .models import Patient
from django.utils.html import format_html

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name_display', 'age', 'genre_display', 'groupe_sanguin', 'contact', 'profession', 'created_at')
    list_filter = ('genre', 'groupe_sanguin', 'created_at')
    search_fields = ('nom', 'prenom', 'npi', 'contact', 'adresse')
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 20
    
    fieldsets = (
        ('Informations personnelles', {
            'fields': ('nom', 'prenom', 'age', 'npi', 'genre', 'profession')
        }),
        ('Informations médicales', {
            'fields': ('groupe_sanguin', 'allergies', 'n_donneur_sang')
        }),
        ('Coordonnées', {
            'fields': ('adresse', 'contact')
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def full_name_display(self, obj):
        # Afficher le nom complet avec un code couleur selon le genre
        color = '#007bff' if obj.genre == 'M' else '#ff69b4'
        return format_html('<span style="color: {};">{}</span>', color, obj.full_name())
    full_name_display.short_description = 'Nom complet'
    
    def genre_display(self, obj):
        # Afficher une icône selon le genre
        if obj.genre == 'M':
            return format_html('<span style="color: #007bff;">♂ Masculin</span>')
        else:
            return format_html('<span style="color: #ff69b4;">♀ Féminin</span>')
    genre_display.short_description = 'Genre'
    
    # Actions personnalisées
    actions = ['export_as_csv']
    
    def export_as_csv(self, request, queryset):
        import csv
        from django.http import HttpResponse
        
        meta = self.model._meta
        field_names = [field.name for field in meta.fields]
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename={meta}-export.csv'
        writer = csv.writer(response)
        
        writer.writerow(field_names)
        for obj in queryset:
            writer.writerow([getattr(obj, field) for field in field_names])
            
        return response
    export_as_csv.short_description = "Exporter les patients sélectionnés en CSV"
