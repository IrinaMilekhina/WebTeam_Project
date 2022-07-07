import datetime
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.http import Http404, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, DeleteView
from orders.forms import CreateOrderForm, FeedbackForm

from orders.models import CategoryOrder, Order, StatusResponse, ResponseOrder
from users.models import Profile
from orders.filters import OrderFilter, CategoryFilter
from django.views import View


class MainView(CreateView):
    template_name = 'orders/main.html'
    title = 'Главная'
    form_class = FeedbackForm
    success_url = reverse_lazy('main')

    def get_context_data(self, **kwargs):
        context = super(MainView, self).get_context_data(**kwargs)
        top_category = CategoryOrder.objects \
            .filter(order__responseorder__statusresponse__status='Approved',
                    order__responseorder__statusresponse__time_status__gte=datetime.datetime.now() - datetime.timedelta(days=7)) \
            .annotate(count=Count('order')) \
            .values('id', 'name', 'image', 'count') \
            .order_by('-count')[:6]

        context['title'] = self.title
        context['categories'] = CategoryOrder.objects.all()
        context['top_categories'] = top_category
        context['form'] = self.form_class

        all_suppliers_amount = len(Profile.objects.filter(role='Supplier'))
        all_categories_amount = len(CategoryOrder.objects.all())
        all_active_orders_amount = len(Order.objects.filter(status='Active'))
        all_customers_amount = len(Profile.objects.filter(role='Customer'))

        context['all_suppliers_amount'] = all_suppliers_amount
        context['all_categories_amount'] = all_categories_amount
        context['all_active_orders_amount'] = all_active_orders_amount
        context['all_customers_amount'] = all_customers_amount
        return context

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        print(form)
        if form.is_valid():
            form.save()
            print(form)
            return redirect(self.success_url)
        return self.form_invalid(form)


class CategoryOrderView(LoginRequiredMixin, ListView):
    model = CategoryOrder
    template_name = 'orders/categories.html'
    paginate_by = 6

    def get_context_data(self, **kwargs):
        context = super(CategoryOrderView, self).get_context_data(**kwargs)
        categories = CategoryOrder.objects.select_related() \
            .filter(is_active=True) \
            .annotate(count_orders=Count('order__responseorder__response_user_id',
                                         filter=Q(order__responseorder__statusresponse__status='Approved'),
                                         distinct=True)) \
            .values('id', 'name', 'image', 'description', 'count_orders')

        context['categories'] = categories

        return context



class Category(LoginRequiredMixin, DetailView):
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

        select_category = CategoryOrder.objects.select_related() \
            .filter(id=self.kwargs['id'])
        category = select_category.annotate(
            count_orders_done=Count('order__responseorder__response_user_id',
                                    filter=Q(order__responseorder__statusresponse__status='Approved'), distinct=True)) \
            .values('id', 'name', 'description', 'is_active', 'image', 'count_orders_done')
        category = category.last()

        return render(request, self.template_name, {'category': category,
                                                    'title': category.get('name'),
                                                    'all_orders_amount': all_orders_amount,
                                                    'all_completed_orders': all_completed_orders,
                                                    'top_suppliers': unique_responses})


class CreateOrder(LoginRequiredMixin, CreateView):
    """Класс-обработчик для создания Заказа"""
    model = Order
    template_name = 'orders/create_order.html'
    form_class = CreateOrderForm
    title = 'Создание заказа'
    success_url = reverse_lazy('main')

    def get(self, request, *args, **kwargs):
        """
        Если приходит id категории в параметрах запроса,
        получаем нужную категорию по id и ставим её дефолтной.
        """

        try:
            category_id = request.GET['category_id']
            category = get_object_or_404(CategoryOrder, id=category_id)
            self.form_class.base_fields['category'].initial = category

            return render(request, self.template_name, {'form': self.form_class, 'title': self.title})
        except (KeyError, Http404):
            return render(request, self.template_name, {'form': self.form_class, 'title': self.title})

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
                                         description=form.data.get(
                                             'description'),
                                         end_time=form.data.get("end_time"))
            order.save()
            # return HttpResponseRedirect(redirect_to=reverse_lazy('main'))
            return redirect('orders:view_order', pk=order.id)

        else:
            return self.form_invalid(form)


class OrderView(LoginRequiredMixin, ListView):
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


class OrderBoardView(LoginRequiredMixin, ListView):
    model = Order
    context_object_name = 'all_orders'
    template_name = 'orders/order_board.html'
    paginate_by = 2

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['all_category'] = CategoryOrder.objects.filter(is_active=True)
        return context


def table_order(request):
    context = {}
    context['filtered_table'] = OrderFilter(
        request.GET, queryset=Order.objects.all())
    # ! Здесь устанавливается пагинация
    paginated = Paginator(context['filtered_table'].qs, 2)
    page_number = request.GET.get('page')
    context['page_obj'] = paginated.get_page(page_number)
    return render(request, 'orders/order_board.html', context=context)


class DeleteCategory(DeleteView):
    model = CategoryOrder
    success_url = reverse_lazy('orders:categories')


def categories(request):
    context = {}
    active_categories = CategoryOrder.objects.select_related() \
                    .filter(is_active=True) \
                .annotate(count_orders=Count('order__responseorder__response_user_id',
                                             filter=Q(order__responseorder__statusresponse__status='Approved'),
                                             distinct=True)) \
                .values('id', 'name', 'image', 'description', 'count_orders')
    all_categories = CategoryOrder.objects.select_related() \
        .annotate(count_orders=Count('order__responseorder__response_user_id',
                                     filter=Q(order__responseorder__statusresponse__status='Approved'),
                                     distinct=True)) \
        .values('id', 'name', 'image', 'description', 'count_orders')
    context['filtered_categories'] = CategoryFilter(
        request.GET, queryset=all_categories)
    context['active_category'] = active_categories
    # ! Здесь устанавливается пагинация
    paginated = Paginator(context['filtered_categories'].qs, 6)
    page_number = request.GET.get('page')
    context['page_obj'] = paginated.get_page(page_number)
    paginated_active = Paginator(context['active_category'], 6)
    page_number_active = request.GET.get('page')
    context['page_obj_active'] = paginated_active.get_page(page_number_active)

    return render(request, 'orders/categories.html', context=context)

class DeleteOrder(DeleteView):
    model = Order
    success_url = reverse_lazy('orders:table_order')


from django.shortcuts import HttpResponse
def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'


def order_confirmation(request, response_pk, order_pk):
    if request.POST:
        statuse_response = get_object_or_404(StatusResponse, id=response_pk)
        statuse_response.status = 'Approved'
        statuse_response.save()
        return redirect(reverse_lazy('orders:view_order', kwargs={'pk': order_pk}))


def order_rejection(request, response_pk, order_pk):
    if request.POST:
        statuse_response = get_object_or_404(StatusResponse, id=response_pk)
        statuse_response.status = 'Not Approved'
        statuse_response.save()
        return redirect(reverse_lazy('orders:view_order', kwargs={'pk': order_pk}))
