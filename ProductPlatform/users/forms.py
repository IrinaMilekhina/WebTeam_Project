from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from users.models import Profile


class PersonalAccountEditForm(forms.ModelForm):
    """Форма для изменения данных в личном кабинете"""
    class Meta:
        model = Profile
        fields = ['username', 'first_name', 'last_name', 'email',
                  'comp_name', 'city', 'ogrn', 'phone_number',
                  'date_joined', 'bio']

    def __init__(self, *args, **kwargs):
        super(PersonalAccountEditForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['readonly'] = True
        self.fields['email'].widget.attrs['readonly'] = True
        self.fields['ogrn'].widget.attrs['readonly'] = True
        self.fields['comp_name'].widget.attrs['readonly'] = True
        self.fields['date_joined'].widget.attrs['readonly'] = True

        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control py-2'


class UserLoginForm(AuthenticationForm):
    class Meta:
        model = Profile
        fields = ('username', 'password')

    def __init__(self, *args, **kwargs):
        super(UserLoginForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['placeholder'] = "Введите имя пользователя"
        self.fields['password'].widget.attrs['placeholder'] = "Введите пароль"
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control py-2'


class UserRegisterForm(UserCreationForm):

    class Meta:
        model = Profile
        fields = ('username', 'email', 'first_name',
                  'last_name', 'password1', 'password2', 'city', 'ogrn', 'comp_name', 'role', 'phone_number', 'bio')

    def __init__(self, *args, **kwargs):
        super(UserRegisterForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['placeholder'] = "Введите Никнейм"
        self.fields['email'].widget.attrs['placeholder'] = "Введите почту"
        self.fields['first_name'].widget.attrs['placeholder'] = "Введите Имя"
        self.fields['last_name'].widget.attrs['placeholder'] = "Введите Фамилию"
        self.fields['password1'].widget.attrs['placeholder'] = "Введите пароль"
        self.fields['password2'].widget.attrs['placeholder'] = "Подтвердите пароль"
        self.fields['city'].widget.attrs['placeholder'] = "Город"
        self.fields['city'].widget.attrs['readonly'] = "readonly"
        self.fields['ogrn'].widget.attrs['placeholder'] = "ОГРН или ЕГРИП"
        self.fields['comp_name'].widget.attrs['placeholder'] = "Название компании"
        self.fields['comp_name'].widget.attrs['readonly'] = "readonly"
        self.fields['role'].widget.attrs['placeholder'] = "Заказчик/Поставщик"
        self.fields['phone_number'].widget.attrs['placeholder'] = "Контактный телефон"
        self.fields['bio'].widget.attrs['placeholder'] = "Описание"

        for field_name, field in self.fields.items():
            if field_name != 'role':
                field.widget.attrs['class'] = 'form-control py-2'
            else:
                field.widget.attrs['class'] = 'form-select py-2'
