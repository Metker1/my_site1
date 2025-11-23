

from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('kitchen.html/', views.kitchen, name='kitchen'),
    path('play1.html/', views.play1, name='play1'),
    path('play2.html/', views.play2, name='play2'),
    path('play3.html/', views.play3, name='play3'),
    path('play4.html/', views.play4, name='play4'),
    path('play5.html/', views.play5, name='play5'),
    path('play6.html/', views.play6, name='play6'),
    path('tennis.html/', views.tennis, name='tennis'),
    path('rpl.html/', views.rpl, name='rpl'),
    path('rezult_rpl.html/', views.rezult_rpl, name='rezult_rpl'),
    path('turnir.html/', views.turnir, name='turnir_rpl'),
    path('binarnie.html/', views.binarnie, name='binarnie'),
    path('line.html/', views.line, name='line'),
    path('hamster.html/', views.hamster, name='hamster'),
    path('statistic.html/', views.statistic, name='statistic'),
    path('blog1.html/', views.blog1, name='blog1'),
    path('blog2.html/', views.blog2, name='blog2'),
    path('blog3.html/', views.blog3, name='blog3'),
    path('blog4.html/', views.blog4, name='blog4'),
    path('blog5.html/', views.blog5, name='blog5'),
    path('blog6.html/', views.blog6, name='blog6'),
    path('post/<int:post_id>/', views.post_detail, name='post_detail'),
    path('category/<int:category_id>/', views.category_posts, name='category_posts'),


]