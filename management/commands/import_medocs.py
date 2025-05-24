import json
import os
from django.core.management.base import BaseCommand
from prescriptions.models import Medicament

class Command(BaseCommand):
    help = 'Import medicaments from JSON file'
    
    def add_arguments(self, parser):
        parser.add_argument('json_file', nargs='?', type=str, help='Path to JSON file containing medicaments')
    
    def handle(self, *args, **options):
        json_file = options['json_file']
        
        if not json_file:
            # Look in parent directory for medoc.json
            parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
            json_file = os.path.join(parent_dir, 'medoc.json')
            
            if not os.path.exists(json_file):
                self.stdout.write(self.style.ERROR(f'File not found: {json_file}'))
                return
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            count = 0
            for item in data:
                # Skip empty entries
                if not item:
                    continue
                
                # For simple string entries
                if isinstance(item, str):
                    name = item.strip()
                    if name:
                        Medicament.objects.get_or_create(
                            nom=name
                        )
                        count += 1
                
                # For dictionary entries
                elif isinstance(item, dict):
                    name = item.get('nom', '').strip()
                    
                    if not name:
                        continue
                    
                    forme = item.get('forme', '')
                    dosage = item.get('dosage', '')
                    description = item.get('description', '')
                    
                    Medicament.objects.get_or_create(
                        nom=name,
                        defaults={
                            'forme': forme,
                            'dosage': dosage,
                            'description': description
                        }
                    )
                    count += 1
            
            self.stdout.write(self.style.SUCCESS(f'Successfully imported {count} medicaments'))
            
        except json.JSONDecodeError:
            self.stdout.write(self.style.ERROR('Invalid JSON file'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))