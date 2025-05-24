from rest_framework import serializers
from patients.models import Patient
from examinations.models import Consultation, ExamenClinique, ExamenParaclinique
from prescriptions.models import Ordonnance, LignePrescription, Medicament
from doctors.models import Doctor

class DoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = ['id', 'email', 'nom', 'prenom', 'n_ordre', 'specialite', 'contact']
        read_only_fields = ['email']

class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = '__all__'

class ExamenCliniqueSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamenClinique
        exclude = ['created_at', 'updated_at']

class ExamenParacliniqueSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamenParaclinique
        exclude = ['created_at', 'updated_at']

class LignePrescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = LignePrescription
        exclude = ['created_at', 'updated_at']

class OrdonnanceSerializer(serializers.ModelSerializer):
    prescriptions = LignePrescriptionSerializer(many=True, read_only=True)
    
    class Meta:
        model = Ordonnance
        exclude = ['created_at', 'updated_at']
        
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['patient'] = f"{instance.consultation.patient.nom} {instance.consultation.patient.prenom}"
        representation['doctor'] = f"Dr. {instance.consultation.doctor.nom} {instance.consultation.doctor.prenom}"
        return representation

class ConsultationSerializer(serializers.ModelSerializer):
    patient_details = PatientSerializer(source='patient', read_only=True)
    doctor_details = DoctorSerializer(source='doctor', read_only=True)
    
    class Meta:
        model = Consultation
        exclude = ['created_at', 'updated_at']
        
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        
        # Add examens cliniques if exists
        try:
            examen_clinique = instance.examen_clinique
            representation['examen_clinique'] = ExamenCliniqueSerializer(examen_clinique).data
        except ExamenClinique.DoesNotExist:
            representation['examen_clinique'] = None
        
        # Add examens paracliniques
        examens_paracliniques = instance.examens_paracliniques.all()
        representation['examens_paracliniques'] = ExamenParacliniqueSerializer(examens_paracliniques, many=True).data
        
        # Add ordonnance if exists
        try:
            ordonnance = instance.ordonnance
            representation['ordonnance'] = OrdonnanceSerializer(ordonnance).data
        except Ordonnance.DoesNotExist:
            representation['ordonnance'] = None
            
        return representation

class MedicamentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medicament
        fields = '__all__'