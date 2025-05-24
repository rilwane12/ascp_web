import json
import os
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.conf import settings
from prescriptions.models import Medicament
from django.db import transaction

class Command(BaseCommand):
    help = 'Importe les médicaments depuis le fichier medoc.json'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            default='medoc.json',
            help='Chemin vers le fichier JSON contenant les médicaments',
        )

    def handle(self, *args, **options):
        file_path = options['file']
        
        # Vérifier que le fichier existe
        if not os.path.isfile(file_path):
            self.stderr.write(self.style.ERROR(f'Le fichier {file_path} n\'existe pas!'))
            return
        
        # Statistiques d'importation
        stats = {
            'total': 0,
            'imported': 0,
            'updated': 0,
            'errors': 0,
        }
        
        # Lire le fichier JSON
        self.stdout.write(self.style.NOTICE(f'Lecture du fichier {file_path}...'))
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
        except json.JSONDecodeError:
            self.stderr.write(self.style.ERROR('Erreur de format JSON dans le fichier.'))
            return
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Erreur lors de la lecture du fichier: {str(e)}'))
            return
        
        # Vérifier la structure du fichier
        if not isinstance(data, dict) or 'data' not in data or not isinstance(data['data'], list):
            self.stderr.write(self.style.ERROR('Format de fichier invalide. La structure attendue est {"data": [...]}'))
            return
        
        # Importer les médicaments
        self.stdout.write(self.style.NOTICE(f'Importation de {len(data["data"])} médicaments...'))
        
        for item in data['data']:
            stats['total'] += 1
            
            try:
                # Extraire les données
                med_id = item.get('i', '')
                nom = item.get('n', '')
                prix_str = item.get('p', '0')
                
                # Convertir le prix (divisé par 100 car les prix semblent être en centimes)
                try:
                    prix = Decimal(prix_str) / 100
                except:
                    prix = Decimal('0.00')
                
                # Vérifier les données obligatoires
                if not nom:
                    self.stderr.write(self.style.WARNING(f'Médicament ignoré (ID: {med_id}): nom manquant'))
                    stats['errors'] += 1
                    continue
                
                # Rechercher si le médicament existe déjà
                medicament, created = Medicament.objects.update_or_create(
                    nom=nom,
                    defaults={
                        'prix': prix,
                    }
                )
                
                if created:
                    stats['imported'] += 1
                else:
                    stats['updated'] += 1
                    
            except Exception as e:
                self.stderr.write(self.style.ERROR(f'Erreur lors de l\'importation du médicament {item.get("n", "")}: {str(e)}'))
                stats['errors'] += 1
        
        # Afficher les statistiques
        self.stdout.write(self.style.SUCCESS(f'Importation terminée!'))
        self.stdout.write(f'Total traité: {stats["total"]}')
        self.stdout.write(f'Nouveaux médicaments: {stats["imported"]}')
        self.stdout.write(f'Médicaments mis à jour: {stats["updated"]}')
        self.stdout.write(f'Erreurs: {stats["errors"]}')

