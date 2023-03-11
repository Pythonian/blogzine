from django.core.management.base import BaseCommand
from django.utils.text import slugify
from django.utils import timezone
from faker import Faker
from blog.models import Category


class Command(BaseCommand):
    help = 'Creates categories using the Faker library'

    def handle(self, *args, **kwargs):
        fake = Faker()

        for i in range(10):
            name = fake.word()
            slug = slugify(name)
            created = timezone.now()
            updated = timezone.now()

            category = Category.objects.create(
                name=name,
                slug=slug,
                created=created,
                updated=updated
            )

            self.stdout.write(self.style.SUCCESS(f'Successfully created category "{category}"'))
