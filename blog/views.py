from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Comment, Category
from django.core.paginator import Paginator, EmptyPage, \
                                  PageNotAnInteger
from django.views.generic import ListView
from django.contrib.postgres.search import SearchVector, \
                                           SearchQuery, SearchRank
from django.contrib.postgres.search import TrigramSimilarity
from .forms import EmailPostForm, CommentForm, SearchForm
from django.core.mail import send_mail
from django.views.decorators.http import require_POST
from taggit.models import Tag
from django.utils import timezone
from django.db.models import Count, Q
from django.db.models.functions import Random


def home(request):
    latest_posts = Post.published.all()[:8]
    sponsored_post = Post.published.filter(sponsored=True).first()
    categories = Category.objects.all()[:5]
    
    # post_categories = Category.objects.order_by('?')[:3]
    post_categories = Category.objects.annotate(post_count=Count('posts')).filter(post_count__gte=2).order_by('?')[:3]
    # categories = Category.objects.annotate(post_count=Count('post')).filter(post_count__gte=3).order_by('?')[:3]
    context = {}
    for category in post_categories:
        posts = Post.published.filter(category=category)[:3]
        context[category] = posts

    cutoff = timezone.now() - timezone.timedelta(days=7)
    trending_posts = Post.published.annotate(
        views_last_week=Count('page_views', filter=Q(
        publish__gte=cutoff))).order_by('-views_last_week')[:5]
    return render(request,
                 'home.html',
                 {'latest_posts': latest_posts,
                  'sponsored_post': sponsored_post,
                  'trending_posts': trending_posts,
                  'post_categories': post_categories,
                  'context': context,
                  'categories': categories})


def post(request, year, month, day, post):
    post = get_object_or_404(Post,
                             status=Post.Status.PUBLISHED,
                             slug=post,
                             publish__year=year,
                             publish__month=month,
                             publish__day=day)

    # List of active comments for this post
    comments = post.comments.filter(active=True)
    # Form for users to comment
    form = CommentForm()

    # List of similar posts
    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_posts = Post.published.filter(tags__in=post_tags_ids)\
                                  .exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=Count('tags'))\
                                .order_by('-same_tags','-publish')[:4]

    return render(request,
                  'post.html',
                  {'post': post,
                   'comments': comments,
                   'form': form,
                   'similar_posts': similar_posts})


def archive(request):
    posts = Post.published.all()
    return render(request, 'archive.html', {'posts': posts})


def post_share(request, post_id):
    # Retrieve post by id
    post = get_object_or_404(Post, id=post_id, \
                                   status=Post.Status.PUBLISHED)
    sent = False

    if request.method == 'POST':
        # Form was submitted
        form = EmailPostForm(request.POST)
        if form.is_valid():
            # Form fields passed validation
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = f"{cd['name']} recommends you read " \
                      f"{post.title}"
            message = f"Read {post.title} at {post_url}\n\n" \
                      f"{cd['name']}\'s comments: {cd['comments']}"
            send_mail(subject, message, 'your_account@gmail.com',
                      [cd['to']])
            sent = True

    else:
        form = EmailPostForm()
    return render(request, 'blog/post/share.html', {'post': post,
                                                    'form': form,
                                                    'sent': sent})


@require_POST
def post_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id, \
                                   status=Post.Status.PUBLISHED)
    comment = None
    # A comment was posted
    form = CommentForm(data=request.POST)
    if form.is_valid():
        # Create a Comment object without saving it to the database
        comment = form.save(commit=False)
        # Assign the post to the comment
        comment.post = post
        # Save the comment to the database
        comment.save()
    return render(request, 'blog/post/comment.html',
                           {'post': post,
                            'form': form,
                            'comment': comment})


def post_search(request):
    form = SearchForm()
    query = None
    results = []

    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            results = Post.published.annotate(
                similarity=TrigramSimilarity('title', query),
            ).filter(similarity__gt=0.1).order_by('-similarity')

    return render(request,
                  'blog/post/search.html',
                  {'form': form,
                   'query': query,
                   'results': results})
