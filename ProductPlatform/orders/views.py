from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView

from orders.forms import CreateOrderForm
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


class CreateOrder(CreateView):
    """Класс-обработчик для создания Заказа"""
    model = Order
    template_name = 'orders/create_order.html'
    form_class = CreateOrderForm
    title = 'Создание заказа'
    success_url = reverse_lazy('main')

    def post(self, request, *args, **kwargs):

        session_user = request.user
        if session_user.get_username() == '':
            return HttpResponseRedirect(redirect_to=reverse_lazy('users:register'))
        form = self.get_form()
        category = CategoryOrder.objects.get(id=int(form.data.get('category')))
        if form.is_valid():
            order = Order.objects.create(author_id=session_user.id,
                                         category=category,
                                         name=form.data.get('name'),
                                         description=form.data.get('description'),
                                         end_time=f'{form.data.get("end_time_year")}-'
                                                  f'{form.data.get("end_time_month")}-'
                                                  f'{form.data.get("end_time_day")}')
            order.save()
            return HttpResponseRedirect(redirect_to=reverse_lazy('main'))
        else:
            return self.form_invalid(form)
