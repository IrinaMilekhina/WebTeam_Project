from django.db import models

from users.models import Profile


class CategoryOrder(models.Model):
    '''Категории заказов'''
    name = models.CharField(max_length=64, unique=True, verbose_name='Название категории')
    # slug = models.SlugField(unique=True)
    is_active = models.BooleanField('active', default=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='category_order/%Y/%m/%d/', blank=True)

    class Meta:
        verbose_name = 'Категория заказа'
        verbose_name_plural = 'Категории заказов'

    def __str__(self):
        return f'{self.name}'


class Order(models.Model):
    '''Заказ'''
    status_choice = [
        ('Active', 'Активно'),
        ('Not Active', 'Не активно')
    ]
    author = models.ForeignKey(Profile, on_delete=models.CASCADE, verbose_name='Компания')
    category = models.ForeignKey(CategoryOrder, on_delete=models.PROTECT, verbose_name='Категория')
    name = models.CharField(max_length=120, verbose_name='Название')
    description = models.TextField(verbose_name='Описание заказа')
    # quantity = models.IntegerField(verbose_name='Количество')
    status = models.CharField(choices=status_choice,
                              max_length=120, verbose_name='Статус')
    create_at = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField()

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def __str__(self):
        return f'{self.category} {self.name}, Заказ создал: {self.author}'


class ResponseOrder(models.Model):
    '''Отклик на заказ'''
    status_choice = [
        ('On Approval', 'На согласовании'),
        ('Approved', 'Утвержден'),
        ('Not Approved', 'Не утвержден'),
        ('Cancelled', 'Отменен')
    ]
    order = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name='Заказ')
    response_user = models.ForeignKey(Profile, on_delete=models.CASCADE, verbose_name='Компания')
    offer = models.TextField(verbose_name='Предложение')
    status = models.CharField(choices=status_choice,
                              max_length=120, verbose_name='Статус')
    create_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Отклик'
        verbose_name_plural = 'Отклики'

    def __str__(self):
        return f'Предлжение от {self.response_user}: {self.offer}, ' \
               f'к заказу - {self.order} со статусом - {self.status}'
