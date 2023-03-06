from django.urls import path

from .views import home, post, search, tag


urlpatterns = [
    path('post/', post, name='post'),
    path('search/', search, name='search'),
    path('tag/', tag, name='tag'),
    path('', home, name='home'),
]