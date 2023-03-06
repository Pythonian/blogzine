from django.urls import path

from .views import home, search, tag


urlpatterns = [
    path('search/', search, name='search'),
    path('tag/', tag, name='tag'),
    path('', home, name='home'),
]