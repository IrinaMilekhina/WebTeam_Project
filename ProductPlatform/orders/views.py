from django.http import HttpResponse, Http404
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from orders.models import CategoryOrder, Order
from django.views import View

class MainView(View):
    template_name = 'orders/main.html'
    title = 'Главная'

    def get(self, request, *args, **kwargs):
        content = {
            'title': self.title,
            'categories': CategoryOrder.objects.all().order_by('-id')[:6]
        }

        return render(request, self.template_name, content)


class CategoryOrderView(ListView):
    model = CategoryOrder
    queryset = CategoryOrder.objects.filter(is_active=True)
    context_object_name = 'all_categories'
    template_name = 'orders/categories.html'
    paginate_by = 5


class Category(DetailView):
    """Класс-обработчик для отображения выбранной категории"""
    model = CategoryOrder
    template_name = 'orders/category.html'

    def get(self, request, *args, **kwargs):
        """Если приходит GET запрос, получаем категорию по id и рендерим шаблон orders/category.html"""
        try:
            id = kwargs.get('id', None)
        except KeyError as err:
            print(err)  # для DEBAG = True
            return render(request, self.template_name, {'ERROR': 'Страница не найдена', 'title': '404'})
        try:
            category = get_object_or_404(CategoryOrder, id=id)
        except Http404 as err:
            print(err)  # для DEBAG = True
            return render(request, self.template_name, {'ERROR': 'Страница не найдена', 'title': '404'})
        return render(request, self.template_name, {'category': category, 'title': category.name})


class OrderView(ListView):
    model = Order
    queryset = Order.objects.all()
    context_object_name = 'active_orders'
    template_name = 'orders/order_board.html'
    paginate_by = 10
