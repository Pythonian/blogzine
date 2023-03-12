from django.shortcuts import render, get_object_or_404
from .models import Post, Category
from django.utils import timezone
from django.db.models import Count, Q
from .utils import mk_paginator


def home(request):
    latest_posts = Post.published.all()[:6]
    sponsored_post = Post.published.filter(sponsored=True).first()
    categories = Category.objects.annotate(post_count=Count('posts')).filter(post_count__gte=1).order_by('?')[:5]
    
    post_categories = Category.objects.annotate(post_count=Count('posts')).filter(post_count__gte=3).order_by('?')[:3]
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

    similar_posts = Post.objects.filter(category=post.category.id).exclude(id=post.id)[:4]

    return render(request,
                  'post.html',
                  {'post': post,
                   'similar_posts': similar_posts})


def archive(request):
    posts = Post.published.all()
    posts = mk_paginator(request, posts, 12)
    return render(request, 'archive.html', {'posts': posts})


def category(request, slug):
    category = get_object_or_404(Category, slug=slug)
    posts = category.posts.all()
    return render(request, 'category.html', {'category': category, 'posts': posts})


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
