from django.contrib.auth.management.commands import createsuperuser
from django.core.management import CommandError

class Command(createsuperuser.Command):
    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument(
            '--n_ordre',
            dest='n_ordre',
            help='Numéro ordre for the superuser account',
        )
        parser.add_argument(
            '--nom',
            dest='nom',
            help='Nom for the superuser account',
        )
        parser.add_argument(
            '--prenom',
            dest='prenom',
            help='Prénom for the superuser account',
        )

    def handle(self, *args, **options):
        n_ordre = options.get('n_ordre')
        nom = options.get('nom')
        prenom = options.get('prenom')
        
        if not options.get('interactive') and not n_ordre:
            raise CommandError('You must use --n_ordre with --noinput.')
        
        if not options.get('interactive') and not nom:
            raise CommandError('You must use --nom with --noinput.')
            
        if not options.get('interactive') and not prenom:
            raise CommandError('You must use --prenom with --noinput.')
            
        options.setdefault('n_ordre', n_ordre)
        options.setdefault('nom', nom)
        options.setdefault('prenom', prenom)
        
        return super().handle(*args, **options)