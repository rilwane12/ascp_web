from django.urls import path, include
from rest_framework import routers
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from . import views

router = routers.DefaultRouter()
router.register(r'patients', views.PatientViewSet)
router.register(r'consultations', views.ConsultationViewSet)
router.register(r'prescriptions', views.OrdonnanceViewSet)
router.register(r'medicaments', views.MedicamentViewSet)
router.register(r'doctors', views.DoctorViewSet)
router.register(r'dashboard', views.DashboardStatsView, basename='dashboard')

urlpatterns = [
    path('', include(router.urls)),
    # Traditional DRF auth
    path('auth/', include('rest_framework.urls', namespace='rest_framework')),
    # JWT auth
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
]