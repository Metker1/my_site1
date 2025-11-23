from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField('Название', max_length=100)

    def __str__(self):
        return self.name


class Post(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Черновик'),
        ('published', 'Опубликовано'),
        ('rejected', 'Отклонено'),
    ]

    title = models.CharField('Заголовок', max_length=200)
    short_text = models.TextField('Краткое описание', max_length=300)
    full_text = models.TextField('Полный текст')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='Категория')
    image = models.ImageField('Картинка', upload_to='posts/', blank=True)
    created = models.DateTimeField('Дата', auto_now_add=True)
    status = models.CharField('Статус', max_length=10, choices=STATUS_CHOICES, default='draft')
    views = models.IntegerField('Просмотры', default=0)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created']


class Idea(models.Model):
    STATUS_CHOICES = [
        ('proposed', 'Предложена'),
        ('under_review', 'На рассмотрении'),
        ('accepted', 'Принята'),
        ('rejected', 'Отклонена'),
        ('implemented', 'Реализована'),
    ]

    title = models.CharField('Название идеи', max_length=200)
    description = models.TextField('Описание идеи')
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Автор')
    created = models.DateTimeField('Дата создания', auto_now_add=True)
    updated = models.DateTimeField('Дата обновления', auto_now=True)
    status = models.CharField('Статус', max_length=15, choices=STATUS_CHOICES, default='proposed')
    notes = models.TextField('Комментарии администратора', blank=True, null=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created']
        verbose_name = 'Идея'
        verbose_name_plural = 'Идеи'