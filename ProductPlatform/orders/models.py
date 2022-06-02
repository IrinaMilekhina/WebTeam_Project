from django.db import models
from users.models import Profile


class CategoryOrder(models.Model):
    name = models.CharField(max_length=64, unique=True, verbose_name='Название категории')
    # slug = models.SlugField(unique=True)
    is_active = models.BooleanField('active', default=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Категория заказа'
        verbose_name_plural = 'Категории заказов'

    def __str__(self):
        return self.name


class Order(models.Model):
    author = models.ForeignKey(Profile, on_delete=models.CASCADE, verbose_name='Компания')
    category = models.ForeignKey(CategoryOrder, on_delete=models.PROTECT, verbose_name='Категория')
    name = models.CharField(max_length=120, verbose_name='Название')
    description = models.TextField(verbose_name='Описание заказа')
    # quantity = models.IntegerField(verbose_name='Количество')
    status = models.BooleanField(default=True)
    create_at = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField()

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def __str__(self):
        return f'{self.category} {self.name}, Заказ создал: {self.author}'
