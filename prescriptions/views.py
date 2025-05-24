from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils import timezone
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
import datetime
import qrcode
import base64
from io import BytesIO

from .models import Ordonnance, LignePrescription, Medicament
from .forms import OrdonnanceForm, LignePrescriptionForm, MedicamentForm
from examinations.models import Consultation

# Génération de PDFs
from django.template.loader import get_template
from xhtml2pdf import pisa
import io

@login_required
def prescription_list(request):
    """Liste des ordonnances avec filtrage"""
    # Récupérer toutes les ordonnances
    ordonnances = Ordonnance.objects.filter(
        consultation__doctor=request.user
    ).order_by('-date_prescription')
    
    # Recherche
    search_query = request.GET.get('search', '')
    if search_query:
        ordonnances = ordonnances.filter(
            Q(consultation__patient__nom__icontains=search_query) | 
            Q(consultation__patient__prenom__icontains=search_query)
        )
    
    # Filtrage par période
    date_range = request.GET.get('date_range', '')
    if date_range:
        today = datetime.date.today()
        if date_range == 'today':
            ordonnances = ordonnances.filter(date_prescription__date=today)
        elif date_range == 'yesterday':
            yesterday = today - datetime.timedelta(days=1)
            ordonnances = ordonnances.filter(date_prescription__date=yesterday)
        elif date_range == 'week':
            start_of_week = today - datetime.timedelta(days=today.weekday())
            ordonnances = ordonnances.filter(date_prescription__date__gte=start_of_week)
        elif date_range == 'month':
            start_of_month = datetime.date(today.year, today.month, 1)
            ordonnances = ordonnances.filter(date_prescription__date__gte=start_of_month)
        elif date_range == 'year':
            start_of_year = datetime.date(today.year, 1, 1)
            ordonnances = ordonnances.filter(date_prescription__date__gte=start_of_year)
    
    # Filtrage par médicament
    medication_id = request.GET.get('medication', '')
    if medication_id:
        try:
            medication_id = int(medication_id)
            ordonnances = ordonnances.filter(
                prescriptions__medicament__icontains=Medicament.objects.get(id=medication_id).nom
            ).distinct()
        except (ValueError, Medicament.DoesNotExist):
            pass
    
    # Pagination
    paginator = Paginator(ordonnances, 10)  # 10 ordonnances par page
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # Liste des médicaments pour le filtre
    medications = Medicament.objects.all().order_by('nom')
    
    return render(request, 'prescriptions/prescription_list.html', {
        'ordonnances': page_obj,
        'medications': medications,
        'search_query': search_query
    })

@login_required
def prescription_create(request, consultation_id):
    """Création d'une nouvelle ordonnance pour une consultation"""
    consultation = get_object_or_404(Consultation, pk=consultation_id, doctor=request.user)
    
    # Vérifier si une ordonnance existe déjà pour cette consultation
    try:
        ordonnance = Ordonnance.objects.get(consultation=consultation)
        messages.warning(request, "Une ordonnance existe déjà pour cette consultation.")
        return redirect('prescription_edit', pk=ordonnance.pk)
    except Ordonnance.DoesNotExist:
        pass
    
    if request.method == 'POST':
        form = OrdonnanceForm(request.POST)
        if form.is_valid():
            ordonnance = form.save(commit=False)
            ordonnance.consultation = consultation
            ordonnance.date_prescription = timezone.now()
            ordonnance.save()
            messages.success(request, "L'ordonnance a été créée avec succès.")
            return redirect('prescription_edit', pk=ordonnance.pk)
    else:
        form = OrdonnanceForm()
    
    return render(request, 'prescriptions/prescription_form.html', {
        'form': form,
        'consultation': consultation
    })

@login_required
def prescription_detail(request, pk):
    """Détail d'une ordonnance"""
    ordonnance = get_object_or_404(
        Ordonnance,
        pk=pk,
        consultation__doctor=request.user
    )
    prescription_lines = ordonnance.prescriptions.all()
    
    return render(request, 'prescriptions/prescription_detail.html', {
        'ordonnance': ordonnance,
        'prescription_lines': prescription_lines
    })

@login_required
def prescription_edit(request, pk):
    """Édition d'une ordonnance existante"""
    ordonnance = get_object_or_404(
        Ordonnance,
        pk=pk,
        consultation__doctor=request.user
    )
    prescription_lines = ordonnance.prescriptions.all()
    
    if request.method == 'POST':
        # Ajouter une nouvelle ligne de prescription
        form = LignePrescriptionForm(request.POST)
        if form.is_valid():
            ligne = form.save(commit=False)
            ligne.ordonnance = ordonnance
            ligne.save()
            messages.success(request, "Médicament ajouté à l'ordonnance.")
            return redirect('prescription_edit', pk=ordonnance.pk)
    else:
        form = LignePrescriptionForm()
    
    # Liste des médicaments disponibles pour l'autocomplétion
    medicaments = Medicament.objects.all().values_list('nom', flat=True)
    
    return render(request, 'prescriptions/prescription_edit.html', {
        'ordonnance': ordonnance,
        'prescription_lines': prescription_lines,
        'form': form,
        'medicaments': list(medicaments)
    })

@login_required
def ligne_prescription_delete(request, pk):
    """Suppression d'une ligne de prescription"""
    ligne = get_object_or_404(LignePrescription, pk=pk, ordonnance__consultation__doctor=request.user)
    ordonnance_pk = ligne.ordonnance.pk
    
    if request.method == 'POST':
        ligne.delete()
        messages.success(request, "Le médicament a été retiré de l'ordonnance.")
    
    return redirect('prescription_edit', pk=ordonnance_pk)

@login_required
def prescription_pdf(request, pk):
    """Génération du PDF de l'ordonnance"""
    ordonnance = get_object_or_404(
        Ordonnance,
        pk=pk,
        consultation__doctor=request.user
    )
    
    # Récupérer les lignes de prescription
    prescription_lines = ordonnance.prescriptions.all()
    
    # Générer le contenu du QR code
    doctor = ordonnance.consultation.doctor
    patient = ordonnance.consultation.patient
    
    # Liste des noms de médicaments
    medication_names = [line.medicament for line in prescription_lines]
    
    # Construction du texte du QR code
    qr_text = f"Médecin: {doctor.nom} {doctor.prenom}, N° Ordre: {doctor.n_ordre}\n"
    qr_text += f"Patient: {patient.nom} {patient.prenom}\n"
    qr_text += f"Médicaments: {', '.join(medication_names)}"
    
    # Génération du QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=3,  # Reduced from 10 to 3 (70% reduction)
        border=2,    # Reduced from 4 to 2 to maintain proportions
    )
    qr.add_data(qr_text)
    qr.make(fit=True)
    
    # Création de l'image QR code
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Conversion de l'image en base64 pour l'inclure dans le HTML
    buffered = BytesIO()
    img.save(buffered)
    qr_code_img = base64.b64encode(buffered.getvalue()).decode()
    
    # Contexte pour le template
    context = {
        'ordonnance': ordonnance,
        'prescription_lines': prescription_lines,
        'date': ordonnance.date_prescription,
        'patient': patient,
        'doctor': doctor,
        'qr_code_img': qr_code_img
    }
    
    # Création du template et rendu avec contexte
    template = get_template('prescriptions/prescription_pdf.html')
    html = template.render(context)
    
    # Création du PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="ordonnance_{ordonnance.pk}.pdf"'
    
    # Génération du PDF
    pdf_buffer = io.BytesIO()
    pdf = pisa.pisaDocument(io.BytesIO(html.encode("UTF-8")), pdf_buffer)
    
    if not pdf.err:
        # Si le PDF est généré avec succès
        pdf_value = pdf_buffer.getvalue()
        response.write(pdf_value)
        
        # Sauvegarder l'image de l'ordonnance si elle n'existe pas déjà
        if not ordonnance.image:
            try:
                from PIL import Image
                import tempfile
                import os
                from django.core.files.base import ContentFile
                
                # Convertir le PDF en image
                try:
                    from pdf2image import convert_from_bytes
                    images = convert_from_bytes(pdf_value)
                    if images:
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
                            images[0].save(tmp.name, 'PNG')
                            with open(tmp.name, 'rb') as f:
                                filename = f"{ordonnance.consultation.patient.nom}_{ordonnance.consultation.patient.prenom}_{timezone.now().strftime('%Y_%m_%d_%H_%M_%S')}.png"
                                ordonnance.image.save(filename, ContentFile(f.read()))
                            os.unlink(tmp.name)
                except Exception as e:
                    messages.error(request, f"Erreur lors de la conversion du PDF en image: {str(e)}")
            except Exception as e:
                messages.error(request, f"Erreur lors de la sauvegarde de l'image: {str(e)}")
        
        return response
    
    # En cas d'erreur
    messages.error(request, "Erreur lors de la génération du PDF")
    return redirect('prescription_detail', pk=pk)

@login_required
def medicament_list(request):
    """Liste des médicaments disponibles"""
    search_query = request.GET.get('search', '')
    if search_query:
        medicaments = Medicament.objects.filter(
            Q(nom__icontains=search_query) | 
            Q(description__icontains=search_query)
        ).order_by('nom')
    else:
        medicaments = Medicament.objects.all().order_by('nom')
    
    # Pagination
    paginator = Paginator(medicaments, 15)  # 15 médicaments par page
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'prescriptions/medicament_list.html', {
        'medicaments': page_obj,
        'search_query': search_query
    })

@login_required
def medicament_create(request):
    """Création d'un nouveau médicament"""
    if request.method == 'POST':
        form = MedicamentForm(request.POST)
        if form.is_valid():
            medicament = form.save()
            messages.success(request, f"Le médicament '{medicament.nom}' a été ajouté avec succès.")
            
            # Rediriger selon le bouton cliqué
            if 'save_and_add' in request.POST:
                return redirect('medicament_create')
            return redirect('medicament_list')
    else:
        form = MedicamentForm()
    
    return render(request, 'prescriptions/medicament_form.html', {'form': form})

@login_required
def medicament_edit(request, pk):
    """Édition d'un médicament existant"""
    medicament = get_object_or_404(Medicament, pk=pk)
    
    if request.method == 'POST':
        form = MedicamentForm(request.POST, instance=medicament)
        if form.is_valid():
            medicament = form.save()
            messages.success(request, f"Le médicament '{medicament.nom}' a été mis à jour avec succès.")
            return redirect('medicament_list')
    else:
        form = MedicamentForm(instance=medicament)
    
    return render(request, 'prescriptions/medicament_form.html', {
        'form': form,
        'medicament': medicament
    })