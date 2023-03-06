from django.shortcuts import render

# Create your views here.
def home(request):

    return render(request, 'home.html', {})


def tag(request):

    return render(request, 'tag.html', {})


def search(request):

    return render(request, 'search.html', {})


def post(request):

    return render(request, 'post.html', {})