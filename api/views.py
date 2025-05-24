from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework_simplejwt.views import TokenObtainPairView
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta

from patients.models import Patient
from examinations.models import Consultation, ExamenClinique, ExamenParaclinique
from prescriptions.models import Ordonnance, Medicament, LignePrescription
from doctors.models import Doctor
from .serializers import (
    PatientSerializer, ConsultationSerializer, 
    OrdonnanceSerializer, MedicamentSerializer,
    DoctorSerializer, ExamenCliniqueSerializer,
    ExamenParacliniqueSerializer, LignePrescriptionSerializer
)

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # For consultations and ordonnances, check if the doctor is the owner
        if hasattr(obj, 'doctor'):
            return obj.doctor == request.user
        
        # For ordonnances, check through consultation
        if hasattr(obj, 'consultation'):
            return obj.consultation.doctor == request.user
        
        # Default deny
        return False

class PatientViewSet(viewsets.ModelViewSet):
    """API endpoint for patients"""
    queryset = Patient.objects.all().order_by('-created_at')
    serializer_class = PatientSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['genre', 'groupe_sanguin']
    search_fields = ['nom', 'prenom', 'contact', 'npi', 'allergies']
    ordering_fields = ['nom', 'prenom', 'age', 'created_at']
    
    def get_queryset(self):
        """Only return patients that the user has consulted"""
        return Patient.objects.filter(
            consultations__doctor=self.request.user
        ).distinct().order_by('-created_at')
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get patient statistics"""
        doctor = request.user
        patients_count = Patient.objects.filter(
            consultations__doctor=doctor
        ).distinct().count()
        
        # Patients by gender
        patients_by_gender = Patient.objects.filter(
            consultations__doctor=doctor
        ).values('genre').annotate(count=Count('id'))
        
        # Recent patients (last 30 days)
        recent_patients_count = Patient.objects.filter(
            consultations__doctor=doctor,
            created_at__gte=timezone.now() - timedelta(days=30)
        ).distinct().count()
        
        return Response({
            'total': patients_count,
            'by_gender': {item['genre']: item['count'] for item in patients_by_gender},
            'recent': recent_patients_count
        })

class ConsultationViewSet(viewsets.ModelViewSet):
    """API endpoint for consultations"""
    queryset = Consultation.objects.all().order_by('-date')
    serializer_class = ConsultationSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['patient']
    search_fields = ['patient__nom', 'patient__prenom']
    ordering_fields = ['date', 'created_at']
    
    def get_queryset(self):
        """Only return consultations that belong to the user"""
        return Consultation.objects.filter(
            doctor=self.request.user
        ).order_by('-date')
    
    def perform_create(self, serializer):
        serializer.save(doctor=self.request.user)
        
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get consultation statistics"""
        doctor = request.user
        consultations_count = Consultation.objects.filter(
            doctor=doctor
        ).count()
        
        # Consultations by date (last 30 days)
        thirty_days_ago = timezone.now() - timedelta(days=30)
        consultations_by_day = Consultation.objects.filter(
            doctor=doctor,
            date__gte=thirty_days_ago
        ).extra({'day': "date(date)"}).values('day').annotate(count=Count('id')).order_by('day')
        
        # Consultations with and without prescriptions
        consultations_with_prescription = Consultation.objects.filter(
            doctor=doctor, 
            ordonnance__isnull=False
        ).count()
        
        consultations_no_prescription = consultations_count - consultations_with_prescription
        
        # Latest consultation date
        latest_consultation = Consultation.objects.filter(
            doctor=doctor
        ).order_by('-date').first()
        
        latest_date = None
        if latest_consultation:
            latest_date = latest_consultation.date
        
        return Response({
            'total': consultations_count,
            'by_day': {item['day']: item['count'] for item in consultations_by_day},
            'with_prescription': consultations_with_prescription,
            'without_prescription': consultations_no_prescription,
            'latest_date': latest_date
        })

class OrdonnanceViewSet(viewsets.ModelViewSet):
    """API endpoint for prescriptions"""
    queryset = Ordonnance.objects.all().order_by('-date_prescription')
    serializer_class = OrdonnanceSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['consultation__patient']
    search_fields = ['consultation__patient__nom', 'consultation__patient__prenom']
    ordering_fields = ['date_prescription', 'created_at']
    
    def get_queryset(self):
        """Only return prescriptions that belong to the user"""
        return Ordonnance.objects.filter(
            consultation__doctor=self.request.user
        ).order_by('-date_prescription')
        
    @action(detail=True, methods=['get'])
    def download_pdf(self, request, pk=None):
        """Get URL for downloading the prescription PDF"""
        ordonnance = self.get_object()
        if ordonnance.image:
            return Response({
                'pdf_url': request.build_absolute_uri(ordonnance.image.url)
            })
        return Response(
            {'error': 'No PDF available for this prescription'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get prescription statistics"""
        doctor = request.user
        prescriptions_count = Ordonnance.objects.filter(
            consultation__doctor=doctor
        ).count()
        
        # Prescriptions by date (last 30 days)
        thirty_days_ago = timezone.now() - timedelta(days=30)
        prescriptions_by_day = Ordonnance.objects.filter(
            consultation__doctor=doctor,
            date_prescription__gte=thirty_days_ago
        ).extra({'day': "date(date_prescription)"}).values('day').annotate(count=Count('id')).order_by('day')
        
        # Most prescribed medications
        medications = LignePrescription.objects.filter(
            ordonnance__consultation__doctor=doctor
        ).values('medicament').annotate(count=Count('id')).order_by('-count')[:10]
        
        return Response({
            'total': prescriptions_count,
            'by_day': {item['day']: item['count'] for item in prescriptions_by_day},
            'top_medications': list(medications)
        })

class MedicamentViewSet(viewsets.ModelViewSet):
    """API endpoint for medications"""
    queryset = Medicament.objects.all().order_by('nom')
    serializer_class = MedicamentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['forme']
    search_fields = ['nom', 'dosage', 'description']
    ordering_fields = ['nom', 'forme', 'dosage', 'created_at']
    
    @action(detail=False, methods=['get'])
    def autocomplete(self, request):
        """Get medication suggestions for autocomplete"""
        query = request.query_params.get('q', '')
        if len(query) < 2:
            return Response([])
            
        medications = Medicament.objects.filter(
            nom__icontains=query
        ).values_list('nom', flat=True)[:10]
        
        return Response(list(medications))

# Add a Doctor ViewSet
class DoctorViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for doctors information (read-only)"""
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [SearchFilter]
    search_fields = ['nom', 'prenom', 'specialite']
    
    def get_queryset(self):
        """Only return the current user's information"""
        return Doctor.objects.filter(id=self.request.user.id)
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get the current logged-in doctor's information"""
        doctor = request.user
        serializer = self.get_serializer(doctor)
        return Response(serializer.data)

# Dashboard Stats API View
class DashboardStatsView(viewsets.ViewSet):
    """API endpoint for dashboard statistics"""
    permission_classes = [permissions.IsAuthenticated]
    
    def list(self, request):
        """Get dashboard statistics for the current doctor"""
        doctor = request.user
        
        # Patient stats
        patients_count = Patient.objects.filter(
            consultations__doctor=doctor
        ).distinct().count()
        
        # Consultation stats
        consultations_count = Consultation.objects.filter(
            doctor=doctor
        ).count()
        
        # Recent consultations (last 30 days)
        thirty_days_ago = timezone.now() - timedelta(days=30)
        recent_consultations = Consultation.objects.filter(
            doctor=doctor,
            date__gte=thirty_days_ago
        ).count()
        
        # Prescription stats
        prescriptions_count = Ordonnance.objects.filter(
            consultation__doctor=doctor
        ).count()
        
        # Most recent patients
        recent_patients = Patient.objects.filter(
            consultations__doctor=doctor
        ).distinct().order_by('-created_at')[:5]
        
        # Most recent consultations
        recent_consultations_list = Consultation.objects.filter(
            doctor=doctor
        ).order_by('-date')[:5]
        
        return Response({
            'patients': {
                'total': patients_count,
            },
            'consultations': {
                'total': consultations_count,
                'recent': recent_consultations,
            },
            'prescriptions': {
                'total': prescriptions_count,
            }
        })