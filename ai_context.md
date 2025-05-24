# Asclepios Web - AI Context Document

## 1. Project Overview and Purpose

Asclepios Web is a comprehensive medical prescription management system built with Django. It's a web migration of a desktop application called "Asclepios Prescription," designed to help doctors manage patients, consultations, examinations, and generate medical prescriptions.

### Key Features
- Patient management
- Medical consultation tracking
- Clinical and paraclinical examination records
- Prescription generation with PDF export
- User authentication and permission control
- Responsive design for multiple devices

### Target Users
- Doctors and medical professionals
- Healthcare clinics and small practices

## 2. Technical Architecture

### Framework and Language
- Django 5.2.1 (Python web framework)
- Python 3.x

### Frontend
- HTML/CSS
- Bootstrap 5 for responsive design
- Font Awesome 6.4.2 (locally hosted)
- jQuery 3.6.0
- Custom JS

### Database
- SQLite (current development database)
- Models defined using Django ORM

### API
- Django REST Framework 3.16.0
- JWT authentication for API access

### PDF Generation
- xhtml2pdf 0.2.17

### Other Key Dependencies
- Pillow 11.0.0 (image processing)
- django-crispy-forms 2.4 + crispy-bootstrap5
- django-cors-headers 4.7.0
- django-filter 24.1
- pdf2image 1.17.0

## 3. Key Components/Apps

### 1. doctors
- Handles user authentication and doctor profile management
- Custom user model extending Django's AbstractUser
- Contains login, logout, and account management views

### 2. patients
- Manages patient records and demographics
- Includes patient search and filtering capabilities

### 3. examinations
- Handles medical consultations
- Records clinical examinations (vital signs, physical exams, etc.)
- Manages paraclinical examinations (lab tests, imaging, etc.)

### 4. prescriptions
- Manages medical prescriptions
- Includes a comprehensive medication database
- Handles prescription generation and PDF export

### 5. api
- RESTful API exposing application functionality
- JWT authentication for secure access
- Pagination and filtering for resource collections

### 6. management
- Additional management functionality

## 4. Data Models

### doctors
- **Doctor**: Custom user model extending AbstractUser
  - email (primary identifier)
  - n_ordre (medical license number)
  - nom, prenom (name, surname)
  - specialite (specialization)
  - contact
  - photo_profil (profile photo)

### patients
- **Patient**:
  - nom, prenom (name, surname)
  - age
  - npi (patient identifier number)
  - genre (gender)
  - profession
  - adresse (address)
  - contact
  - groupe_sanguin (blood group)
  - allergies
  - created_at, updated_at (timestamps)

### examinations
- **Consultation**:
  - patient (ForeignKey to Patient)
  - doctor (ForeignKey to Doctor)
  - date
  - created_at, updated_at (timestamps)

- **ExamenClinique** (Clinical Examination):
  - consultation (OneToOneField to Consultation)
  - Vital signs (poids, taille, temperature, etc.)
  - Medical history (atcd_med, atcd_chir, atcd_fam)
  - Diagnostic fields

- **ExamenParaclinique** (Paraclinical Examination):
  - consultation (ForeignKey to Consultation)
  - nom (name)
  - description
  - resultat (result)
  - date_demande, date_resultat (request/result dates)

### prescriptions
- **Medicament** (Medication):
  - nom (name)
  - forme (form)
  - dosage
  - description
  - prix (price)

- **Ordonnance** (Prescription):
  - consultation (OneToOneField to Consultation)
  - date_prescription
  - image (for prescription image)

- **LignePrescription** (Prescription Line):
  - ordonnance (ForeignKey to Ordonnance)
  - medicament (medication name)
  - quantite (quantity)
  - posologie (dosage instructions)

## 5. Application Structure

```
asclepios_web/
├── asclepios/           # Main project configuration
├── doctors/             # Doctor/user management
├── patients/            # Patient management
├── examinations/        # Consultations and exams
├── prescriptions/       # Prescriptions and medications
├── api/                 # REST API endpoints
├── management/          # Additional management functionality
├── static/              # Static files (CSS, JS, images, etc.)
│   ├── css/
│   ├── js/
│   ├── images/
│   └── fontawesome/     # Locally hosted Font Awesome
├── templates/           # HTML templates
│   ├── base/
│   ├── doctors/
│   ├── patients/
│   ├── examinations/
│   └── prescriptions/
├── media/               # User-uploaded files
├── staticfiles/         # Collected static files
├── manage.py            # Django command-line utility
├── requirements.txt     # Project dependencies
└── asclepios.db         # SQLite database
```

## 6. Development Environment

### Requirements
- Python 3.x
- Django 5.2.1
- Other dependencies as specified in requirements.txt

### Setup Instructions
1. Clone the repository
2. Create and activate a virtual environment
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```
4. Apply migrations
   ```bash
   python manage.py migrate
   ```
5. Create a superuser (doctor)
   ```bash
   python manage.py shell -c "from doctors.models import Doctor; Doctor.objects.create_superuser(email='admin@example.com', password='yourpassword', n_ordre='ADMIN1234', nom='Admin', prenom='Super')"
   ```
6. Run the development server
   ```bash
   python manage.py runserver
   ```
7. Access the application at http://localhost:8000/

### Development Workflow
- The application follows standard Django MVT architecture
- Templates extend from base templates (templates/base/base.html)
- Static files should be placed in the appropriate static/ directory
- Media files are stored in the media/ directory

## 7. Instructions for AI Usage

When working with AI assistants on this project, consider the following:

### File References
- When referencing files, use absolute paths relative to the project root
- The project root is typically: `/Users/rilwanedjibril/DevMac/asclepios_web/`

### Common Tasks
- **Feature Development**: Describe the feature requirements in detail
- **Bug Fixes**: Provide error messages, relevant code, and expected behavior
- **Code Review**: Share the code you want reviewed and your specific concerns
- **Database Changes**: 
  - For model changes, request generation of corresponding migrations
  - Remember to apply migrations after making model changes

### Best Practices
- Always refer to this context document when starting a new session with an AI assistant
- When implementing new features, maintain the existing code style and architecture
- Follow Django's best practices for model design, views, and URL patterns
- Use Django's class-based views where appropriate

### Language Notes
- The application's interface is entirely in French
- Code comments and variable names are mostly in French
- Documentation can be in either French or English

### Current Challenges/TODOs
- Any ongoing issues or planned features can be documented here

