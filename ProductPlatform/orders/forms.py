from django import forms
from django.forms import SelectDateWidget

from orders.models import Order, Feedback


class CreateOrderForm(forms.ModelForm):
    """Форма для изменения данных в заказе"""

    class Meta:
        model = Order
        fields = ['category', 'name', 'description', 'end_time']
        widgets = {
            'end_time': SelectDateWidget()
        }

    def __init__(self, *args, **kwargs):
        super(CreateOrderForm, self).__init__(*args, **kwargs)
        self.fields['category'].widget.attrs['placeholder'] = "Выбор категории"
        self.fields['name'].widget.attrs['placeholder'] = "Введите продукцию"
        self.fields['description'].widget.attrs['placeholder'] = "Опишите детали заказа"
        self.fields['end_time'].widget.attrs['class'] = "datetimepicker"



class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['name_user', 'email', 'issue', 'message',]

    def __init__(self, *args, **kwargs):
        super(FeedbackForm, self).__init__(*args, **kwargs)
        self.fields['name_user'].widget.attrs['type'] = 'text'
        self.fields['name_user'].widget.attrs['id'] = 'name'
        self.fields['name_user'].widget.attrs['name'] = 'name'
        self.fields['name_user'].widget.attrs['placeholder'] = 'Имя...'
        self.fields['name_user'].widget.attrs['required'] = ''

        self.fields['email'].widget.attrs['type'] = 'text'
        self.fields['email'].widget.attrs['id'] = 'email'
        self.fields['email'].widget.attrs['name'] = 'email'
        self.fields['email'].widget.attrs['placeholder'] = 'Эл. почта...'
        self.fields['email'].widget.attrs['required'] = ''
        self.fields['email'].widget.attrs['pattern'] = '[^ @]*@[^ @]*'

        self.fields['issue'].widget.attrs['type'] = 'text'
        self.fields['issue'].widget.attrs['id'] = 'subject'
        self.fields['issue'].widget.attrs['name'] = 'subject'
        self.fields['issue'].widget.attrs['placeholder'] = 'Тема...'
        self.fields['issue'].widget.attrs['required'] = ''

        self.fields['message'].widget.attrs['name'] = 'user_message'
        self.fields['message'].widget.attrs['class'] = 'form-control'
        self.fields['message'].widget.attrs['id'] = 'user_message'
        self.fields['message'].widget.attrs['placeholder'] = 'Сообщение...'
        self.fields['message'].widget.attrs['required'] = ''