from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.text import slugify
from django.contrib.auth.models import User
from blog.models import Post, Category
from faker import Faker
import random


class Command(BaseCommand):
    help = 'Creates fake posts.'

    def add_arguments(self, parser):
        parser.add_argument('count', type=int, help='Number of posts to create.')

    def handle(self, *args, **options):
        count = options['count']
        fake = Faker()
        users = User.objects.all()
        categories = Category.objects.all()

        for i in range(count):
            title = fake.sentence()
            slug = slugify(title)
            author = random.choice(users)
            category = random.choice(categories)
            excerpt = fake.paragraph()
            body = fake.paragraph()
            publish = fake.date_time_this_year(before_now=True, after_now=False, tzinfo=None)
            status = Post.Status.PUBLISHED
            page_views = fake.random_int(min=1, max=1000)
            read_time = fake.random_int(min=1, max=60)
            sponsored = fake.boolean(chance_of_getting_true=50)
            enable_comments = fake.boolean(chance_of_getting_true=50)

            post = Post.objects.create(title=title, slug=slug, author=author, category=category, excerpt=excerpt,
                                       body=body, publish=publish, status=status, page_views=page_views,
                                       read_time=read_time, sponsored=sponsored, enable_comments=enable_comments)

        self.stdout.write(self.style.SUCCESS(f'Successfully created post {count} posts.'))
