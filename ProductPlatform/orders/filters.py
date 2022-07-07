import django_filters
from orders.models import Order, CategoryOrder


class OrderFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')

    CHOICES = (
        ('fromA', 'От А до Я'),
        ('fromZ', 'От Я до А'),
    )

    ordering_category = django_filters.ChoiceFilter(
        label='Сортировка по продукту', choices=CHOICES, method='filter_by_category')

    class Meta:
        model = Order
        fields = ['category', 'name']

    def filter_by_category(self, queryset, category, value):
        expression = 'name' if value == 'fromA' else '-name'
        return queryset.order_by(expression)


class CategoryFilter(django_filters.FilterSet):
    CHOICES = (
        ('fromA', 'От А до Я'),
        ('fromZ', 'От Я до А'),
    )

    ordering_category = django_filters.ChoiceFilter(
        label='Сортировка по наименованию', choices=CHOICES, method='filter_by_category')

    class Meta:
        model = CategoryOrder
        fields = ['is_active']

    def filter_by_category(self, queryset, category, value):
        expression = 'name' if value == 'fromA' else '-name'
        return queryset.order_by(expression)
