from django.contrib import admin
from django.utils.html import format_html
from .models import Medicament, Ordonnance, LignePrescription

class LignePrescriptionInline(admin.TabularInline):
    model = LignePrescription
    extra = 1
    fields = ('medicament', 'quantite', 'posologie')

@admin.register(Medicament)
class MedicamentAdmin(admin.ModelAdmin):
    list_display = ('id', 'nom', 'forme', 'dosage', 'prix_display', 'created_at')
    list_filter = ('forme', 'created_at')
    search_fields = ('nom', 'description', 'dosage')
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 20
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('nom', 'forme', 'dosage')
        }),
        ('Détails supplémentaires', {
            'fields': ('description', 'prix')
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def prix_display(self, obj):
        if obj.prix:
            return f"{obj.prix} €"
        return "—"
    prix_display.short_description = 'Prix'
    prix_display.admin_order_field = 'prix'

@admin.register(Ordonnance)
class OrdonnanceAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_patient', 'get_doctor', 'date_prescription_display', 'count_prescriptions', 'has_image')
    list_filter = ('date_prescription', 'consultation__doctor')
    search_fields = ('consultation__patient__nom', 'consultation__patient__prenom', 'consultation__doctor__nom')
    readonly_fields = ('created_at', 'updated_at', 'image_preview')
    date_hierarchy = 'date_prescription'
    inlines = [LignePrescriptionInline]
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('consultation', 'date_prescription')
        }),
        ('Image de l\'ordonnance', {
            'fields': ('image', 'image_preview')
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_patient(self, obj):
        patient = obj.consultation.patient
        return format_html('<a href="/admin/patients/patient/{}/change/">{}</a>', 
                         patient.id, patient)
    get_patient.short_description = 'Patient'
    get_patient.admin_order_field = 'consultation__patient'
    
    def get_doctor(self, obj):
        doctor = obj.consultation.doctor
        return format_html('<a href="/admin/doctors/doctor/{}/change/">{}</a>', 
                         doctor.id, doctor)
    get_doctor.short_description = 'Médecin'
    get_doctor.admin_order_field = 'consultation__doctor'
    
    def date_prescription_display(self, obj):
        return obj.date_prescription.strftime('%d/%m/%Y %H:%M')
    date_prescription_display.short_description = 'Date de prescription'
    date_prescription_display.admin_order_field = 'date_prescription'
    
    def count_prescriptions(self, obj):
        count = obj.prescriptions.count()
        return format_html('<span style="font-weight: bold;">{}</span>', count)
    count_prescriptions.short_description = 'Lignes'
    
    def has_image(self, obj):
        if obj.image:
            return format_html('<span style="color: green;">✓</span>')
        return format_html('<span style="color: red;">✗</span>')
    has_image.short_description = 'Image'
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-width: 300px; max-height: 300px;" />', obj.image.url)
        return "Pas d'image"
    image_preview.short_description = 'Aperçu de l\'image'

@admin.register(LignePrescription)
class LignePrescriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'medicament', 'quantite', 'get_ordonnance', 'get_patient', 'created_at')
    list_filter = ('created_at', 'ordonnance__date_prescription')
    search_fields = ('medicament', 'posologie', 'ordonnance__consultation__patient__nom')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Ordonnance', {
            'fields': ('ordonnance',)
        }),
        ('Détails de la prescription', {
            'fields': ('medicament', 'quantite', 'posologie')
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_ordonnance(self, obj):
        return format_html('<a href="/admin/prescriptions/ordonnance/{}/change/">Ordonnance #{}</a>', 
                         obj.ordonnance.id, obj.ordonnance.id)
    get_ordonnance.short_description = 'Ordonnance'
    get_ordonnance.admin_order_field = 'ordonnance'
    
    def get_patient(self, obj):
        patient = obj.ordonnance.consultation.patient
        return format_html('<a href="/admin/patients/patient/{}/change/">{}</a>', 
                         patient.id, patient)
    get_patient.short_description = 'Patient'
    get_patient.admin_order_field = 'ordonnance__consultation__patient'
