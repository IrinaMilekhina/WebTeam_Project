from django.contrib.auth.models import AbstractUser
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField



# Create your models here.


class Profile(AbstractUser):
    company_choice = [
        ('Customer', 'Заказчик'),
        ('Supplier', 'Поставщик')
    ]
    phone_number = PhoneNumberField(verbose_name='Номер телефона', unique=True)
    email = models.EmailField(
        max_length=120, verbose_name='Электронная почта', unique=True)
    city = models.CharField(max_length=120, verbose_name='Город')
    # В шаблоне добавить подсказку количество цифр!
    ogrn = models.CharField(max_length=15, verbose_name='ОГРН', unique=True)
    comp_name = models.CharField(
        max_length=120, unique=True, verbose_name='Название компании')
    role = models.CharField(choices=company_choice,
                            max_length=120, verbose_name='Роль')
    bio = models.TextField(verbose_name='Описание', blank=True, )

    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'

    def __str__(self):
        return f'Название компании: {self.comp_name}'

