from django.db import models
from users.models import Profile


class Category(models.Model):
    name = models.CharField(max_length=120, verbose_name='Название категории')
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Orders(models.Model):
    author = models.ForeignKey('users.Profile', on_delete=models.CASCADE, verbose_name='Компания')
    category = models.ForeignKey(Category, on_delete=models.PROTECT, verbose_name='Категория')
    name = models.CharField(max_length=120, verbose_name='Название')
    description = models.TextField(verbose_name='Описание заказа')
    quantity = models.CharField(max_length=120, verbose_name='Количество')
    status = models.BooleanField(default=True)
    create_at = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField()

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def __str__(self):
        return f'{self.category} {self.name}, Заказ создал: {self.author}'

