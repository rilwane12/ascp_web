from django.contrib import admin
from django.utils.html import format_html
from .models import Consultation, ExamenClinique, ExamenParaclinique

class ExamenCliniqueInline(admin.StackedInline):
    model = ExamenClinique
    can_delete = False
    verbose_name_plural = 'Examen clinique'
    fieldsets = (
        ('Constantes vitales', {
            'fields': (('poids', 'taille'), ('temperature', 'fr_cardiaque'), 
                      ('fr_respiratoire', 'sa_o2'), 'conj_muq')
        }),
        ('Antécédents et plaintes', {
            'fields': ('atcd_med', 'atcd_chir', 'atcd_fam', 'mode_vie', 'plaintes')
        }),
        ('Examens physiques et diagnostics', {
            'fields': ('examen_physique', 'examen_physique_1', 'examen_physique_2', 
                      'examen_physique_3', 'hypothese_diagnostics', 'diagnostics', 'note_medecin')
        }),
    )

class ExamenParacliniqueInline(admin.TabularInline):
    model = ExamenParaclinique
    extra = 0
    fields = ('nom', 'description', 'date_demande', 'date_resultat', 'resultat')

@admin.register(Consultation)
class ConsultationAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient_display', 'doctor_display', 'date_display', 'has_examen_clinique', 'created_at')
    list_filter = ('doctor', 'date', 'created_at')
    search_fields = ('id', 'patient__nom', 'patient__prenom', 'doctor__nom', 'doctor__prenom')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'date'
    inlines = [ExamenCliniqueInline, ExamenParacliniqueInline]
    
    def patient_display(self, obj):
        return format_html('<a href="/admin/patients/patient/{}/change/">{}</a>', 
                         obj.patient.id, obj.patient)
    patient_display.short_description = 'Patient'
    
    def doctor_display(self, obj):
        return format_html('<a href="/admin/doctors/doctor/{}/change/">{}</a>', 
                         obj.doctor.id, obj.doctor)
    doctor_display.short_description = 'Médecin'
    
    def date_display(self, obj):
        return obj.date.strftime('%d/%m/%Y %H:%M')
    date_display.short_description = 'Date de consultation'
    
    def has_examen_clinique(self, obj):
        try:
            if hasattr(obj, 'examen_clinique'):
                return format_html('<span style="color: green;">✓</span>')
            return format_html('<span style="color: red;">✗</span>')
        except ExamenClinique.DoesNotExist:
            return format_html('<span style="color: red;">✗</span>')
    has_examen_clinique.short_description = 'Examen clinique'
    
@admin.register(ExamenClinique)
class ExamenCliniqueAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_patient', 'get_doctor', 'get_consultation_date', 'created_at')
    list_filter = ('consultation__date', 'created_at')
    search_fields = ('consultation__patient__nom', 'consultation__patient__prenom', 'diagnostics')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Consultation', {
            'fields': ('consultation',)
        }),
        ('Constantes vitales', {
            'fields': (('poids', 'taille'), ('temperature', 'fr_cardiaque'), 
                      ('fr_respiratoire', 'sa_o2'), 'conj_muq')
        }),
        ('Antécédents et plaintes', {
            'fields': ('atcd_med', 'atcd_chir', 'atcd_fam', 'mode_vie', 'plaintes')
        }),
        ('Examens physiques et diagnostics', {
            'fields': ('examen_physique', 'examen_physique_1', 'examen_physique_2', 
                      'examen_physique_3', 'hypothese_diagnostics', 'diagnostics', 'note_medecin')
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_patient(self, obj):
        return obj.consultation.patient
    get_patient.short_description = 'Patient'
    get_patient.admin_order_field = 'consultation__patient'
    
    def get_doctor(self, obj):
        return obj.consultation.doctor
    get_doctor.short_description = 'Médecin'
    get_doctor.admin_order_field = 'consultation__doctor'
    
    def get_consultation_date(self, obj):
        return obj.consultation.date.strftime('%d/%m/%Y')
    get_consultation_date.short_description = 'Date de consultation'
    get_consultation_date.admin_order_field = 'consultation__date'

@admin.register(ExamenParaclinique)
class ExamenParacliniqueAdmin(admin.ModelAdmin):
    list_display = ('id', 'nom', 'get_patient', 'date_demande_display', 'date_resultat_display', 'has_resultat')
    list_filter = ('nom', 'date_demande', 'date_resultat')
    search_fields = ('nom', 'description', 'consultation__patient__nom', 'consultation__patient__prenom')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Information de base', {
            'fields': ('consultation', 'nom', 'description')
        }),
        ('Dates', {
            'fields': ('date_demande', 'date_resultat')
        }),
        ('Résultat', {
            'fields': ('resultat',)
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_patient(self, obj):
        return obj.consultation.patient
    get_patient.short_description = 'Patient'
    get_patient.admin_order_field = 'consultation__patient'
    
    def date_demande_display(self, obj):
        return obj.date_demande.strftime('%d/%m/%Y')
    date_demande_display.short_description = 'Date de demande'
    date_demande_display.admin_order_field = 'date_demande'
    
    def date_resultat_display(self, obj):
        if obj.date_resultat:
            return obj.date_resultat.strftime('%d/%m/%Y')
        return '—'
    date_resultat_display.short_description = 'Date de résultat'
    date_resultat_display.admin_order_field = 'date_resultat'
    
    def has_resultat(self, obj):
        if obj.resultat:
            return format_html('<span style="color: green;">✓</span>')
        return format_html('<span style="color: red;">✗</span>')
    has_resultat.short_description = 'Résultat disponible'
