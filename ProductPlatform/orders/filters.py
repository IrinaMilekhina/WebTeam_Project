import django_filters
from orders.models import Order


class OrderFilter(django_filters.FilterSet):

    CHOICES = (
        ('fromA', 'От А до Я'),
        ('fromZ', 'От Я до А'),
    )

    ordering_category = django_filters.ChoiceFilter(
        label='Сортировка по продукту', choices=CHOICES, method='filter_by_category')

    class Meta:
        model = Order
        fields = ['category']

    def filter_by_category(self, queryset, category, value):
        expression = 'name' if value == 'fromA' else '-name'
        return queryset.order_by(expression)
