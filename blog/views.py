
from django.shortcuts import render




def index(request):
    return render(request, 'blog/index.html')

def kitchen(request):
    return render(request, 'blog/kitchen.html')

def play1(request):
    return render(request, 'blog/play1.html')

def play2(request):
    return render(request, 'blog/play2.html')

def play3(request):
    return render(request, 'blog/play3.html')

def play4(request):
    return render(request, 'blog/play4.html')

def play5(request):
    return render(request, 'blog/play5.html')

def play6(request):
    return render(request, 'blog/play6.html')

def tennis(request):
    return render(request, 'blog/tennis.html')

def rpl(request):
    return render(request, 'blog/rpl.html')

def rezult_rpl(request):
    return render(request, 'blog/rezult_rpl.html')

def turnir(request):
    return render(request, 'blog/turnir.html')

def binarnie(request):
    return render(request, 'blog/binarnie.html')

def line(request):
    return render(request, 'blog/line.html')

def hamster(request):
    return render(request, 'blog/hamster.html')

def statistic(request):
    return render(request, 'blog/statistic.html')

def blog1(request):
    return render(request, 'blog/blog1.html')

def blog2(request):
    return render(request, 'blog/blog2.html')

def blog3(request):
    return render(request, 'blog/blog3.html')

def blog4(request):
    return render(request, 'blog/blog4.html')

def blog5(request):
    return render(request, 'blog/blog5.html')

def blog6(request):
    return render(request, 'blog/blog6.html')


from django.shortcuts import render, get_object_or_404
from .models import Post, Category


def post_list(request):
    posts = Post.objects.filter(status='published')
    return render(request, 'blog/post_list.html', {'posts': posts})


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id, status='published')

    # Увеличиваем просмотры
    post.views += 1
    post.save()

    return render(request, 'blog/post_detail.html', {'post': post})


def category_posts(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    posts = Post.objects.filter(category=category, status='published')
    return render(request, 'blog/category_posts.html', {'category': category, 'posts': posts})

