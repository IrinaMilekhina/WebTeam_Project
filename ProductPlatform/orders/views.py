import datetime

from django.db.models import Count, Q
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.core.paginator import Paginator

from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView
from orders.forms import CreateOrderForm

from orders.filters import OrderFilter
from orders.models import CategoryOrder, Order
from users.models import Profile
from django.views import View


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
    template_name = 'orders/categories.html'
    paginate_by = 6

    def get_context_data(self, **kwargs):
        context = super(CategoryOrderView, self).get_context_data(**kwargs)
        categories = CategoryOrder.objects.select_related() \
            .filter(is_active=True) \
            .annotate(count_orders=Count('id', filter=Q(order__responseorder__statusresponse__status='Approved'))) \
            .values('id', 'name', 'image', 'description', 'count_orders')

        context['categories'] = categories

        return context


class Category(ListView):
    """Класс-обработчик для отображения выбранной категории"""
    model = CategoryOrder
    template_name = 'orders/category.html'

    def get_context_data(self, **kwargs):
        context = super(Category, self).get_context_data(**kwargs)
        select_category = CategoryOrder.objects.select_related() \
            .filter(id=self.kwargs['id'])
        category = select_category.annotate(
            count_orders_done=Count('id', filter=Q(order__responseorder__statusresponse__status='Approved'))) \
            .values('id', 'name', 'description', 'image', 'count_orders_done')
        context['category'] = category.last()

        return context


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
