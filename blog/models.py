from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.contrib.sitemaps import ping_google
from taggit.managers import TaggableManager
from django.utils.html import strip_tags
from .utils import get_read_time


class Category(models.Model):
    name = models.CharField(_('name'), max_length=20, unique=True)
    slug = models.SlugField(_('slug'), max_length=20, unique=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('category', kwargs={'slug': self.slug})


class PublishedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset()\
                      .filter(status=Post.Status.PUBLISHED)


class Post(models.Model):

    class Status(models.TextChoices):
        DRAFT = 'DF', 'Draft'
        PUBLISHED = 'PB', 'Published'

    title = models.CharField(_('title'), max_length=250)
    slug = models.SlugField(_('slug'), max_length=250,
                            unique_for_date='publish')
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               verbose_name=_('author'),
                               related_name='posts')
    category = models.ForeignKey(Category,
                                 on_delete=models.PROTECT,
                                 verbose_name=_('category'),
                                 related_name='posts')
    excerpt = models.CharField(_('excerpt'), max_length=250)
    body = models.TextField(_('body'))
    image = models.ImageField(upload_to='posts',
                              verbose_name=_('image'), default='default.jpg')
    image_caption = models.CharField(_('image caption'),
                                     blank=True, max_length=50)
    publish = models.DateTimeField(default=timezone.now)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=2,
                              choices=Status.choices,
                              default=Status.DRAFT)
    page_views = models.PositiveIntegerField(
        _('page views'), default=0)
    read_time = models.PositiveIntegerField(
        _('read time'), default=0,
        help_text='Estimated time taken to read the post.')
    sponsored = models.BooleanField(
        default=False)
    enable_comments = models.BooleanField(
        default=True)

    objects = models.Manager()
    published = PublishedManager()
    tags = TaggableManager()

    class Meta:
        ordering = ['-publish']
        get_latest_by = 'publish'
        verbose_name = _('post')
        verbose_name_plural = _('posts')
        indexes = [
            models.Index(fields=['-publish']),
        ]

    def __str__(self):
        return self.title
    
    def get_page_views_last_week(self):
        """Calculates the number of page views for a post in the last 7 days"""
        cutoff = timezone.now() - timezone.timedelta(days=7)
        # count the number of page views that occured after the cutoff date
        views = self.post.filter(publish__gte=cutoff).count()
        return views

    def get_absolute_url(self):
        return reverse('post',
                       args=[self.publish.year,
                             self.publish.month,
                             self.publish.day,
                             self.slug])
    
    def get_previous_post(self):
        return self.get_previous_by_publish(status=Post.Status.PUBLISHED)

    def get_next_post(self):
        return self.get_next_by_publish(status=Post.Status.PUBLISHED)
    
    def save(self, *args, **kwargs):
        if not self.excerpt:
            self.excerpt = self.body[:140]

        if self.body:
            self.read_time = get_read_time(self.body)

        # When a post has been sponsored, update the
        # other existing sponsored post as False
        if self.sponsored:
            sponsored_post = Post.objects.filter(
                sponsored=True).exclude(pk=self.pk)
            if sponsored_post.exists():
                sponsored_post.update(sponsored=False)

        super().save(*args, **kwargs)

        # Ping google due to sitemap changes that
        # arises from a new Post being created.
        try:
            ping_google()
        except Exception:
            pass

    @property
    def word_count(self):
        return len(strip_tags(self.body).split())


class Comment(models.Model):
    post = models.ForeignKey(Post,
                             on_delete=models.CASCADE,
                             related_name='comments')
    name = models.CharField(max_length=80)
    email = models.EmailField()
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ['created']
        indexes = [
            models.Index(fields=['created']),
        ]

    def __str__(self):
        return f'Comment by {self.name} on {self.post}'
