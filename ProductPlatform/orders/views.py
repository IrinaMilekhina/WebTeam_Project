import datetime
from django.core.paginator import Paginator
from django.db.models import Count
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, DeleteView
from orders.forms import CreateOrderForm
from orders.filters import OrderFilter
from orders.models import CategoryOrder, Order
from django.views import View

from users.models import Profile


class MainView(View):
    template_name = 'orders/main.html'
    title = 'Главная'

    def get(self, request, *args, **kwargs):
        top_category = CategoryOrder.objects \
                           .filter(order__responseorder__statusresponse__status='Approved',
                                   order__responseorder__statusresponse__time_status__gte=
                                   datetime.datetime.now() - datetime.timedelta(days=7)) \
                           .annotate(count=Count('order')) \
                           .values('id', 'name', 'count') \
                           .order_by('-count')[:6]
        content = {
            'title': self.title,
            'categories': CategoryOrder.objects.all(),
            'top_categories': top_category
        }

        return render(request, self.template_name, content)


class CategoryOrderView(ListView):
    model = CategoryOrder
    # queryset = CategoryOrder.objects.filter(is_active=True)
    context_object_name = 'all_categories'
    template_name = 'orders/categories.html'
    paginate_by = 6

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        all_category = CategoryOrder.objects.select_related().all()
        current_profile = Profile.objects.select_related().get(pk=self.request.user.pk)
        context['all_category'] = all_category
        context['active_category'] = all_category.filter(is_active=True)
        context['user'] = current_profile

        return context


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


class OrderView(ListView):
    """Класс-обработчик для просмотра заказа"""
    model = Order
    template_name = 'orders/view_order.html'

    def get(self, request, *args, **kwargs):
        try:
            id = kwargs.get('pk', None)
        except KeyError as err:
            print(err)
        try:
            order = get_object_or_404(Order, id=id)
        except Http404 as err:
            print(err)
        response_orders = order.responseorder_set.all()
        context = {
            'order': order,
            'response_orders': response_orders,
        }
        return render(request, self.template_name, context=context)


class OrderBoardView(ListView):
    model = Order
    context_object_name = 'all_orders'
    template_name = 'orders/order_board.html'
    paginate_by = 2

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['all_category'] = CategoryOrder.objects.filter(is_active=True)
        return context


def HomeView(request):
    context = {}
    filtered_persons = OrderFilter(request.GET, queryset=Order.objects.all())
    context['all_category'] = CategoryOrder.objects.filter(is_active=True)
    context['filtered_persons'] = filtered_persons
    # ! Здесь устанавливается пагинация
    paginated = Paginator(filtered_persons.qs, 2)
    page_number = request.GET.get('page')
    person_page_obj = paginated.get_page(page_number)
    context['page_obj'] = person_page_obj
    return render(request, 'orders/order_board.html', context=context)


class DeleteCategory(DeleteView):
    model = CategoryOrder
    success_url = reverse_lazy('orders:categories')
    template_name = 'orders/delete_category.html'

    # def delete(self, request, *args, **kwargs):
    #     self.object = self.get_object()
    #     if self.object.is_active:
    #         self.object.is_active = False
    #         self.object.product_set.update(is_active=False)
    #     else:
    #         self.object.is_active = True
    #     self.object.save()
    #     return HttpResponseRedirect(self.get_success_url())
