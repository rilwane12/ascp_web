import os
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
from django.conf import settings



from .models import Ordonnance, LignePrescription, Medicament
from .forms import OrdonnanceForm, LignePrescriptionForm, MedicamentForm
from examinations.models import Consultation

# Génération de PDFs
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm, mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.lib import colors
from reportlab.platypus import Paragraph
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
from PIL import Image as PILImage
from reportlab.pdfbase.pdfmetrics import stringWidth

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

# Fonction utilitaire pour dessiner du texte avec alignement
def draw_text(canvas_obj, x, y, text, font_name="Helvetica", font_size=12, align="left"):
    """
    Dessine du texte sur le canvas avec l'alignement spécifié.
    
    Args:
        canvas_obj: L'objet canvas ReportLab
        x: Position horizontale
        y: Position verticale
        text: Texte à dessiner
        font_name: Nom de la police
        font_size: Taille de la police
        align: Alignement du texte ('left', 'center', ou 'right')
    """
    canvas_obj.setFont(font_name, font_size)
    if align == "center":
        text_width = canvas_obj.stringWidth(text, font_name, font_size)
        x = x - (text_width / 2)
    elif align == "right":
        text_width = canvas_obj.stringWidth(text, font_name, font_size)
        x = x - text_width
    canvas_obj.drawString(x, y, text)

@login_required
def prescription_pdf(request, pk):
    """Génération du PDF de l'ordonnance avec ReportLab"""
    # Import os module explicitly to avoid scope issues
    import os
    
    ordonnance = get_object_or_404(
        Ordonnance,
        pk=pk,
        consultation__doctor=request.user
    )
    
    # Récupérer les lignes de prescription
    prescription_lines = ordonnance.prescriptions.all()
    
    # Récupérer les informations du médecin et du patient
    doctor = ordonnance.consultation.doctor
    patient = ordonnance.consultation.patient
    
    # Liste des noms de médicaments pour le QR code
    medication_names = [line.medicament for line in prescription_lines]
    
    # Construction du texte du QR code
    qr_text = f"Médecin: {doctor.nom} {doctor.prenom}, N° Ordre: {doctor.n_ordre}\n"
    qr_text += f"Patient: {patient.nom} {patient.prenom}\n"
    qr_text += f"Médicaments: {', '.join(medication_names)}"
    
    # Génération du QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=3,  # Taille réduite pour l'adaptation
        border=2,
    )
    qr.add_data(qr_text)
    qr.make(fit=True)
    
    # Création de l'image QR code
    qr_img = qr.make_image(fill_color="black", back_color="white")
    qr_img_buffer = BytesIO()
    qr_img.save(qr_img_buffer)
    qr_img_buffer.seek(0)
    
    # Création du PDF avec ReportLab
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="ordonnance_{ordonnance.pk}.pdf"'
    
    # Création du buffer pour le PDF
    pdf_buffer = BytesIO()
    
    # Définition des dimensions et marges
    page_width, page_height = A4
    margin = 1.5 * cm  # Marge de 1.5cm
    
    # Création du canvas
    p = canvas.Canvas(pdf_buffer, pagesize=A4)
    
    # ----- EN-TÊTE -----
    current_y = page_height - margin
    
    # Logo Caducée à gauche (80x80px)
    # image_path = os.path.join(settings.STATIC_ROOT, 'images', 'caduce.png')
    # logo_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'caduce.png')
    logo_path = os.path.join(settings.STATIC_ROOT, 'images', 'caduce.png')
    try:
        p.drawImage(logo_path, margin, current_y - 80, width=80, height=80, mask='auto')
    except Exception as e:
        # Fallback en cas d'erreur avec l'image
        p.rect(margin, current_y - 80, 80, 80, stroke=1, fill=0)
        draw_text(p, margin + 40, current_y - 40, "Logo", "Helvetica", 10, "center")
    
    # Titre "ORDONNANCE" centré dans un cadre noir
    title_text = "ORDONNANCE"
    title_width = stringWidth(title_text, "Helvetica-Bold", 20)
    title_padding = 20  # Padding horizontal du titre
    title_height = 40   # Hauteur du cadre du titre
    
    # Position du titre centré
    title_x = (page_width / 2)
    title_y = current_y - 40  # Centré verticalement dans les 80px du haut
    
    # Dessiner le cadre
    p.setStrokeColor(colors.black)
    p.setLineWidth(2)
    p.rect(title_x - (title_width/2) - title_padding, 
           title_y - 15, 
           title_width + (2 * title_padding), 
           title_height, 
           stroke=1, fill=0)
    
    # Dessiner le texte du titre
    draw_text(p, title_x, title_y, title_text, "Helvetica-Bold", 20, "center")
    
    # QR Code à droite (80x80px)
    qr_x = page_width - margin - 80
    p.drawImage(ImageReader(qr_img_buffer), qr_x, current_y - 80, width=80, height=80)
    
    # Date sous le QR code en italique
    date_formatted = ordonnance.date_prescription.strftime("%Y-%m-%d %H:%M:%S")
    draw_text(p, qr_x + 40, current_y - 90, date_formatted, "Helvetica-Oblique", 10, "center")
    
    # ----- INFORMATIONS MÉDECIN (20px sous l'en-tête) -----
    current_y = current_y - 80 - 20  # 80px pour l'en-tête + 20px d'espacement
    
    # Nom et prénom du médecin
    draw_text(p, margin, current_y, f"Dr {doctor.nom} {doctor.prenom}", "Helvetica-Bold", 18)
    current_y -= 15
    
    # Spécialité
    specialite = doctor.specialite or "Médecine générale"
    draw_text(p, margin, current_y, specialite, "Helvetica", 12)
    current_y -= 15
    
    # Numéro d'ordre
    draw_text(p, margin, current_y, f"N° d'Ordre : {doctor.n_ordre}", "Helvetica", 12)
    current_y -= 15
    
    # Contact
    contact = doctor.contact or ""
    draw_text(p, margin, current_y, f"Contact : {contact}", "Helvetica", 12)
    current_y -= 20  # Espacement avant le tableau patient
    
    # ----- TABLEAU PATIENT (20px sous info médecin) -----
    table_width = page_width - 2 * margin
    
    # Définition des largeurs de colonnes
    col_width_label = 80
    col_width = (table_width - 2 * col_width_label) / 2
    
    # Hauteur de ligne du tableau
    row_height = 20
    
    # Nombre de lignes du tableau (2 ou 3 si adresse présente)
    table_rows = 3 if patient.adresse else 2
    
    # Dessiner le cadre extérieur du tableau
    p.setStrokeColor(colors.black)
    p.setLineWidth(1)
    p.rect(margin, current_y - (row_height * table_rows), table_width, row_height * table_rows)
    
    # Variables pour tracer les cellules du tableau
    table_top = current_y
    table_left = margin
    
    # Première ligne: Nom et Prénom
    # Ligne horizontale après la première ligne
    p.line(table_left, table_top - row_height, 
           table_left + table_width, table_top - row_height)
    
    # Lignes verticales
    p.line(table_left + col_width_label, table_top, 
           table_left + col_width_label, table_top - row_height)
    p.line(table_left + col_width_label + col_width, table_top, 
           table_left + col_width_label + col_width, table_top - row_height)
    p.line(table_left + col_width_label + col_width + col_width_label, table_top, 
           table_left + col_width_label + col_width + col_width_label, table_top - row_height)
    
    # Deuxième ligne: Sexe et Age
    p.line(table_left + col_width_label, table_top - row_height, 
           table_left + col_width_label, table_top - 2 * row_height)
    p.line(table_left + col_width_label + col_width, table_top - row_height, 
           table_left + col_width_label + col_width, table_top - 2 * row_height)
    p.line(table_left + col_width_label + col_width + col_width_label, table_top - row_height, 
           table_left + col_width_label + col_width + col_width_label, table_top - 2 * row_height)
    
    if table_rows > 2:
        # Ligne horizontale pour l'adresse
        p.line(table_left, table_top - 2 * row_height, 
               table_left + table_width, table_top - 2 * row_height)
        
        # Ligne verticale pour l'adresse
        p.line(table_left + col_width_label, table_top - 2 * row_height, 
               table_left + col_width_label, table_top - 3 * row_height)
    
    # Texte dans les cellules
    # Première ligne
    p.setFillColorRGB(0.97, 0.97, 0.97)  # Couleur de fond pour les labels
    p.rect(table_left, table_top - row_height, col_width_label, row_height, stroke=0, fill=1)
    p.rect(table_left + col_width_label + col_width, table_top - row_height, 
           col_width_label, row_height, stroke=0, fill=1)
    
    # Deuxième ligne
    p.rect(table_left, table_top - 2 * row_height, col_width_label, row_height, stroke=0, fill=1)
    p.rect(table_left + col_width_label + col_width, table_top - 2 * row_height, 
           col_width_label, row_height, stroke=0, fill=1)
    
    # Troisième ligne si adresse
    if table_rows > 2:
        p.rect(table_left, table_top - 3 * row_height, col_width_label, row_height, stroke=0, fill=1)
    
    p.setFillColor(colors.black)
    
    # Texte de la première ligne
    draw_text(p, table_left + 5, table_top - row_height + 5, "Nom :", "Helvetica-Bold", 12)
    draw_text(p, table_left + col_width_label + 5, table_top - row_height + 5, patient.nom)
    draw_text(p, table_left + col_width_label + col_width + 5, table_top - row_height + 5, "Prénom(s) :", "Helvetica-Bold", 12)
    draw_text(p, table_left + col_width_label + col_width + col_width_label + 5, table_top - row_height + 5, patient.prenom)
    
    # Texte de la deuxième ligne
    genre = "M" if patient.genre == "M" else "F"
    draw_text(p, table_left + 5, table_top - 2 * row_height + 5, "Sexe :", "Helvetica-Bold", 12)
    draw_text(p, table_left + col_width_label + 5, table_top - 2 * row_height + 5, genre)
    draw_text(p, table_left + col_width_label + col_width + 5, table_top - 2 * row_height + 5, "Age :", "Helvetica-Bold", 12)
    draw_text(p, table_left + col_width_label + col_width + col_width_label + 5, table_top - 2 * row_height + 5, patient.age)
    
    # Texte de la troisième ligne si adresse
    if table_rows > 2:
        draw_text(p, table_left + 5, table_top - 3 * row_height + 5, "Adresse :", "Helvetica-Bold", 12)
        draw_text(p, table_left + col_width_label + 5, table_top - 3 * row_height + 5, patient.adresse)
    
    # Mettre à jour la position verticale après le tableau
    current_y = table_top - (row_height * table_rows) - 25  # 25px d'espacement après le tableau
    
    # ----- SECTION PRESCRIPTION -----
    # Titre "PRESCRIPTION" avec ligne en dessous
    draw_text(p, margin, current_y, "PRESCRIPTION", "Helvetica-Bold", 16)
    current_y -= 7
    p.setLineWidth(2)
    p.line(margin, current_y, page_width - margin, current_y)
    current_y -= 35  # Espacement avant les lignes de prescription
    
    # Dessiner les lignes de prescription
    if prescription_lines:
        for i, ligne in enumerate(prescription_lines, 1):
            # Numéro et nom du médicament
            p.setFont("Helvetica-Bold", 13)
            p.drawString(margin, current_y, f"{i}.")
            p.drawString(margin + 20, current_y, ligne.medicament)
            
            # Quantité (alignée à droite)
            if ligne.quantite:
                quantite_width = p.stringWidth(ligne.quantite, "Helvetica-Bold", 12)
                p.drawString(page_width - margin - quantite_width, current_y, ligne.quantite)
            
            current_y -= 15
            
            # Posologie (en italique et indentée)
            p.setFont("Helvetica-Oblique", 12)
            p.drawString(margin + 25, current_y, ligne.posologie)
            current_y -= 50  # Espacement entre les médicaments
    else:
        # Message si aucun médicament prescrit
        p.setFont("Helvetica-Oblique", 14)
        p.setFillColor(colors.gray)
        text = "Aucun médicament prescrit"
        text_width = p.stringWidth(text, "Helvetica-Oblique", 14)
        p.drawString((page_width - text_width) / 2, current_y - 50, text)
        p.setFillColor(colors.black)
    
    # ----- PIED DE PAGE -----
    # Note pharmacien (centrée en bas de page)
    footer_text = "Le médicament est l'affaire de votre pharmacien"
    p.setFont("Helvetica-Oblique", 11)
    text_width = p.stringWidth(footer_text, "Helvetica-Oblique", 11)
    p.drawString((page_width - text_width) / 2, margin + 5, footer_text) #
    
    # Signature
    signature_y = margin + 80  # Position y pour la section signature
    
    # Texte "Signature du médecin" aligné à droite
    # p.setFont("Helvetica", 12)
    # signature_text = "Signature du médecin"
    # text_width = p.stringWidth(signature_text, "Helvetica", 12)
    # p.drawString(page_width - margin - text_width, signature_y, signature_text)
    
    # Espace pour la signature
    signature_y -= 50
    
    # Nom du médecin sous l'espace de signature
    doctor_signature = f"Dr. {doctor.nom} {doctor.prenom}"
    p.setFont("Helvetica-Bold", 12)
    text_width = p.stringWidth(doctor_signature, "Helvetica-Bold", 12)
    p.drawString(page_width - margin - text_width, signature_y, doctor_signature)
    
    # Finaliser le PDF
    p.showPage()
    p.save()
    
    # Récupérer le contenu du PDF
    pdf_value = pdf_buffer.getvalue()
    response.write(pdf_value)
    
    # Sauvegarder l'image de l'ordonnance si elle n'existe pas déjà
    if not ordonnance.image:
        try:
            import tempfile
            import os
            from PIL import Image
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