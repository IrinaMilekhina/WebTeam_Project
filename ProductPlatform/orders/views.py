import datetime

from django.db.models import Count
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView
from orders.forms import CreateOrderForm

from orders.models import CategoryOrder, Order, StatusResponse, ResponseOrder
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
    queryset = CategoryOrder.objects.filter(is_active=True)
    context_object_name = 'all_categories'
    template_name = 'orders/categories.html'
    paginate_by = 6


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
        orders = Order.objects.filter(category_id=category.pk, status='Active')
        all_orders_amount = len(orders)
        status_response_orders = StatusResponse.objects.filter(status='Approved')
        response_orders = [status_response.response_order for status_response in status_response_orders]
        run_orders = [response_order.order for response_order in response_orders if response_order.order.status == 'Active' and response_order.order.category == category]
        all_completed_orders = len(run_orders)
        top_suppliers = [response_order.response_user for response_order in response_orders if response_order.order.status == 'Active' and response_order.order.category == category]

        all_responses = ResponseOrder.objects.select_related().all()
        active_responses = all_responses.filter(order__category=category)
        unique_responses = {}
        for i in active_responses:
            if not i.statusresponse_set.last() is None and i.statusresponse_set.last().status == 'Approved':

                if unique_responses.get(i.response_user):
                    unique_responses[i.response_user] = unique_responses[i.response_user] + 1
                else:
                    unique_responses[i.response_user] = 1

        # unique_responses = sorted(unique_responses.items(), key=lambda item: item[1])[::-5]

        return render(request, self.template_name, {'category': category,
                                                    'title': category.name,
                                                    'all_orders_amount': all_orders_amount,
                                                    'all_completed_orders': all_completed_orders,
                                                    'top_suppliers': unique_responses})


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


class OrderBoardViewFilter(ListView):
    model = Order
    context_object_name = 'all_orders'
    template_name = 'orders/order_board.html'
    paginate_by = 2

    def get_queryset(self, **kwargs):
        qs = super().get_queryset(**kwargs)
        return qs.filter(category=self.kwargs['id'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['all_category'] = CategoryOrder.objects.filter(is_active=True)
        return context
