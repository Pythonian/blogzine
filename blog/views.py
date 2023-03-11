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
from .utils import mk_paginator


def home(request):
    latest_posts = Post.published.all()[:8]
    sponsored_post = Post.published.filter(sponsored=True).first()
    categories = Category.objects.annotate(post_count=Count('posts')).filter(post_count__gte=1).order_by('?')[:5]
    
    post_categories = Category.objects.annotate(post_count=Count('posts')).filter(post_count__gte=2).order_by('?')[:3]
    context = {}
    for category in post_categories:
        posts = Post.published.filter(category=category)[:3]
        context[category] = posts

    cutoff = timezone.now() - timezone.timedelta(days=7)
    trending_posts = Post.published.annotate(
        views_last_week=Count('page_views', filter=Q(
        publish__gte=cutoff))).order_by('-views_last_week')[:5]
    
    most_viewed_posts = Post.published.order_by('-page_views')[:4]

    return render(request,
                 'home.html',
                 {'latest_posts': latest_posts,
                  'sponsored_post': sponsored_post,
                  'trending_posts': trending_posts,
                  'post_categories': post_categories,
                  'context': context,
                  'most_viewed_posts': most_viewed_posts,
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
    posts = mk_paginator(request, posts, 12)
    return render(request, 'archive.html', {'posts': posts})


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
    posts = ''
    query = request.GET.get('q', None)
    post_count = 0
    if query:
        posts = Post.objects.filter(Q(title__icontains=query) | Q(body__icontains=query))
        post_count = posts.count()
    context = {
        'posts': posts,
        'query': query,
        'post_count': post_count,
    }

    return render(request,
                  'search.html', context)
