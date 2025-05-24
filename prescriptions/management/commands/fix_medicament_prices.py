from django.core.management.base import BaseCommand
from prescriptions.models import Medicament
from django.db.models import F
from decimal import Decimal

class Command(BaseCommand):
    help = 'Fix medicament prices by multiplying by 100 (convert from Euros to FCFA)'

    def handle(self, *args, **options):
        # Get all medications with prices
        medicaments_with_price = Medicament.objects.filter(prix__isnull=False)
        count = medicaments_with_price.count()
        
        if count == 0:
            self.stdout.write(self.style.WARNING('No medications with prices found.'))
            return
        
        # Show a sample of prices before conversion
        sample = medicaments_with_price.order_by('?')[:5]  # random sample of 5
        self.stdout.write(self.style.SUCCESS('Sample of prices before conversion:'))
        for med in sample:
            self.stdout.write(f'  - {med.nom}: {med.prix} €')
        
        # Update all prices by multiplying by 100
        updated = 0
        for medicament in medicaments_with_price:
            old_price = medicament.prix
            medicament.prix = old_price * 100
            medicament.save()
            updated += 1
            
        self.stdout.write(self.style.SUCCESS(f'Successfully updated {updated} medication prices.'))
        
        # Show the same sample after conversion
        self.stdout.write(self.style.SUCCESS('Sample after conversion (now in FCFA):'))
        for med in Medicament.objects.filter(id__in=[m.id for m in sample]):
            self.stdout.write(f'  - {med.nom}: {med.prix} FCFA')

