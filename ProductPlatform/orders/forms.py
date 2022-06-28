from django import forms
from django.forms import SelectDateWidget, DateInput

from orders.models import Order


class CreateOrderForm(forms.ModelForm):
    """Форма для изменения данных в заказе"""

    class Meta:
        model = Order
        fields = ['category', 'name', 'description', 'end_time']
        widgets = {
            'end_time': (DateInput(attrs={'type': 'date'}))
        }

    def __init__(self, *args, **kwargs):
        super(CreateOrderForm, self).__init__(*args, **kwargs)

        self.fields['name'].widget.attrs['placeholder'] = "Введите наименование заказа"
        self.fields['name'].widget.attrs['class'] = "form-control"
        self.fields['name'].widget.attrs['aria-describedby'] = "inputGroup-sizing-sm"

        self.fields['category'].widget.attrs['placeholder'] = "Выберите категорию"
        self.fields['category'].widget.attrs['class'] = "form-select"
        self.fields['category'].widget.attrs['aria-describedby'] = "inputGroup-sizing-sm"

        self.fields['end_time'].widget.attrs['class'] = "form-control"

        self.fields['description'].widget.attrs['placeholder'] = "Опишите детали заказа"
        self.fields['description'].widget.attrs['class'] = "form-control"