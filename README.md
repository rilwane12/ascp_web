# Asclepios Web - Système de Gestion d'Ordonnances Médicales

Asclepios Web est une application de gestion d'ordonnances médicales basée sur Django, permettant aux médecins de gérer les patients, consultations, examens et prescriptions médicales.

## Caractéristiques

- Gestion des patients (ajout, modification, consultation)
- Gestion des consultations médicales
- Enregistrement des examens cliniques et paracliniques
- Création d'ordonnances avec génération de PDF
- Interface responsive avec Bootstrap 5
- Authentification sécurisée pour les médecins

## Installation

1. Cloner le dépôt
```bash
git clone <repository-url>
cd asclepios_web
```

2. Créer et activer un environnement virtuel (recommandé)
```bash
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate
```

3. Installer les dépendances
```bash
pip install -r requirements.txt
```

4. Appliquer les migrations
```bash
python manage.py migrate
```

5. Créer un superutilisateur
```bash
python manage.py shell -c "from doctors.models import Doctor; Doctor.objects.create_superuser(email='admin@example.com', password='votremotdepasse', n_ordre='ADMIN1234', nom='Admin', prenom='Super')"
```

6. Lancer le serveur de développement
```bash
python manage.py runserver
```

## Structure du projet

```
asclepios_web/
├── asclepios/           # Configuration principale du projet
├── doctors/             # Application de gestion des médecins/utilisateurs
├── patients/            # Application de gestion des patients
├── examinations/        # Application de gestion des consultations et examens
├── prescriptions/       # Application de gestion des ordonnances
├── static/              # Fichiers statiques (CSS, JavaScript, images)
├── templates/           # Templates HTML
├── media/               # Fichiers téléchargés (ordonnances générées, etc.)
└── manage.py            # Script de gestion Django
```

## Technologies utilisées

- Django 5.2
- Bootstrap 5
- xhtml2pdf (pour la génération de PDF)
- SQLite (base de données par défaut)

## Utilisation

1. Accédez à l'application via http://localhost:8000/
2. Connectez-vous avec vos identifiants médecin
3. Utilisez le tableau de bord pour accéder aux différentes fonctionnalités

## Migration à partir de l'application bureau

Cette application web est une migration de l'application bureau Asclepios Prescription, offrant les mêmes fonctionnalités mais avec l'avantage d'être accessible depuis n'importe quel appareil avec un navigateur web.

## Licence

Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus de détails.