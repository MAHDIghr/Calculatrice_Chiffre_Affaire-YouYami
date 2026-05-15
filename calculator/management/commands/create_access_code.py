from django.core.management.base import BaseCommand
from calculator.models import AccessCode

class Command(BaseCommand):
    help = 'Crée le code d\'accès au site'

    def add_arguments(self, parser):
        parser.add_argument('code', type=str, help='Le code d\'accès')

    def handle(self, *args, **kwargs):
        code = kwargs['code']
        
        if len(code) < 8:
            self.stdout.write(self.style.ERROR('Le code doit faire au moins 8 caractères'))
            return
        
        access = AccessCode()
        access.set_code(code)
        access.save()
        
        self.stdout.write(self.style.SUCCESS(f'Code d\'accès créé avec succès !'))