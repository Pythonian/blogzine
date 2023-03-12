from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Create a new superuser'

    def handle(self, *args, **options):
        User.objects.create_superuser(username='admin', email='admin', password='admin')

        self.stdout.write(self.style.SUCCESS('Superuser created successfully!'))
