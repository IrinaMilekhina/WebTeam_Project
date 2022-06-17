from django import forms
from django.forms import SelectDateWidget

from orders.models import Order



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


    # def __init__(self, *args, **kwargs):
    #     super(CreateOrderForm, self).__init__(*args, **kwargs)
    #     self.fields['username'].widget.attrs['readonly'] = True
    #     self.fields['email'].widget.attrs['readonly'] = True
    #     self.fields['ogrn'].widget.attrs['readonly'] = True
    #     self.fields['role'].widget.attrs['readonly'] = True
    #     self.fields['date_joined'].widget.attrs['readonly'] = True
