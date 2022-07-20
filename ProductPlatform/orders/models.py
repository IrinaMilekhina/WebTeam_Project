from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver

from users.models import Profile


class CategoryOrder(models.Model):
    '''Категории заказов'''
    name = models.CharField(max_length=64, unique=True, verbose_name='Название категории')
    # slug = models.SlugField(unique=True)
    is_active = models.BooleanField('active', default=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='category_order/%Y/%m/%d/',
                              default='category_order/default/placeholder_300x150.png', blank=True)

    class Meta:
        verbose_name = 'Категория заказа'
        verbose_name_plural = 'Категории заказов'

    def __str__(self):
        return f'{self.name}'

    def delete(self, using=None, keep_parents=False):
         if self.is_active == True:
             self.is_active = False
         elif self.is_active == False:
             self.is_active = True
         self.save()


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
                              max_length=120, default='Active', verbose_name='Статус')
    create_at = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def __str__(self):
        return f'{self.category} {self.name}, Заказ создал: {self.author}'

    def save(self, *args, **kwargs):
        super(Order, self).save(*args, **kwargs)
        if self.status == 'Not Active':
            set_responses = StatusResponse.objects.filter(response_order_id=self.id)
            for response in set_responses:
                if response.status == 'On Approval':
                    response.status = 'Not Approved'
                    response.save()

    def delete(self, using=None, keep_parents=False):
         if self.status == 'Active':
             self.status = 'Not Active'
         elif self.status == 'Not Active':
             self.status = 'Active'
         self.save()


class ResponseOrder(models.Model):
    '''Отклик на заказ'''

    order = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name='Заказ')
    response_user = models.ForeignKey(Profile, on_delete=models.CASCADE, verbose_name='Компания')
    price = models.FloatField(default=0, verbose_name='Цена')
    offer = models.TextField(verbose_name='Предложение')
    create_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Отклик'
        verbose_name_plural = 'Отклики'

    def __str__(self):
        return f'Предлжение от {self.response_user}: {self.offer}, ' \
               f'к заказу - {self.order}'

    def save(self, *args, **kwargs):
        super(ResponseOrder, self).save(*args, **kwargs)
        obj = StatusResponse.objects.create(response_order=self,
                                            status='On Approval',
                                            user_initiator=self.response_user)
        obj.save()

    

class StatusResponse(models.Model):
    '''Статус отклика для избежания UPDATE таблицы RESPONSE_ORDER'''
    status_choice = [
        ('On Approval', 'На согласовании'),
        ('Approved', 'Утвержден'),
        ('Not Approved', 'Не утвержден'),
        ('Cancelled', 'Отменен')
    ]

    response_order = models.ForeignKey(ResponseOrder, on_delete=models.CASCADE, verbose_name='Отклик на заказ')
    status = models.CharField(choices=status_choice,
                              max_length=120, verbose_name='Статус')
    time_status = models.DateTimeField(auto_now_add=True)
    user_initiator = models.ForeignKey(Profile, on_delete=models.CASCADE, verbose_name='Пользователь инициатор')

    class Meta:
        verbose_name = 'Статус отклика'
        verbose_name_plural = 'Статусы откликов'

    def __str__(self):
        return f'У отклика с ID# {self.response_order} статус - {self.status}'

    def save(self, *args, **kwargs):
        super(StatusResponse, self).save(*args, **kwargs)
        if self.status == 'Approved':
            obj = Order.objects.get(id=self.response_order.order_id)
            obj.status = 'Not Active'
            obj.save()


class Feedback(models.Model):
    name_user = models.CharField(max_length=50, verbose_name='Имя пользователя')
    email = models.EmailField(verbose_name='Почта')
    issue = models.CharField(max_length=250, verbose_name='Тема')
    message = models.TextField(verbose_name='Сообщение')

    class Meta:
        verbose_name = 'Сообщение от пользователя'
        verbose_name_plural = 'Сообщения от пользователей'

    def __str__(self):
        return f'Сообщение от {self.name_user}'
