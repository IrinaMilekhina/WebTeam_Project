import datetime
from pprint import pprint

from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, DeleteView, UpdateView
from orders.forms import CreateOrderForm, FeedbackForm, ResponseOrderForm
from multi_form_view import MultiModelFormView
from orders.models import CategoryOrder, Order, StatusResponse, ResponseOrder
from users.models import Profile
from orders.filters import OrderFilter, CategoryFilter
from django.views import View
from django.contrib.auth.decorators import login_required, user_passes_test

from orders.decorators import order_board_check


class MainView(CreateView):
    template_name = 'orders/main.html'
    title = 'Главная'
    form_class = FeedbackForm
    success_url = reverse_lazy('main')

    def get_context_data(self, **kwargs):
        context = super(MainView, self).get_context_data(**kwargs)
        top_category = CategoryOrder.objects \
                           .filter(is_active=True,
                                   order__responseorder__statusresponse__status='Approved',
                                   order__responseorder__statusresponse__time_status__gte=datetime.datetime.now() - datetime.timedelta(
                                       days=7)) \
                           .annotate(count=Count('order')) \
                           .values('id', 'name', 'image', 'count', 'description') \
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
                                         filter=Q(
                                             order__responseorder__statusresponse__status='Approved'),
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
        status_response_orders = StatusResponse.objects.filter(
            status='Approved')
        response_orders = [
            status_response.response_order for status_response in status_response_orders]
        run_orders = [response_order.order for response_order in response_orders if response_order.order.status ==
                      'Active' and response_order.order.category == category]
        all_completed_orders = len(run_orders)
        top_suppliers = [response_order.response_user for response_order in response_orders if
                         response_order.order.status ==
                         'Active' and response_order.order.category == category]

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


class CreateOrder(LoginRequiredMixin, UserPassesTestMixin, CreateView):
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
            self.form_class.base_fields['category'].initial = None

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

    def test_func(self):
        return self.request.user.role != 'Supplier'


class OrderView(LoginRequiredMixin, MultiModelFormView):
    """Класс-обработчик для просмотра заказа"""
    model = Order
    template_name = 'orders/view_order.html'
    form_classes = {'response_order': ResponseOrderForm}

    def get(self, request, *args, **kwargs):
        try:
            id = kwargs.get('pk', None)
        except KeyError as err:
            print(err)
        try:
            order = get_object_or_404(Order, id=id)
        except Http404 as err:
            print(err)

        approved_response = StatusResponse.objects.filter(response_order__order=order, status='Approved').last()
        if approved_response:
            approved_response = approved_response.response_order
            no_approved_response = False
        elif StatusResponse.objects.filter(response_order__order=order, status='Cancelled').last():
            no_approved_response = True
            cancelled_response = True
        else:
            no_approved_response = True

        response_orders = order.responseorder_set.all()
        # print(response_orders)
        responses = []
        not_active_responses_order_users_id = []

        if request.user.role == 'Customer':
            for response_order in response_orders:
                response_statuses = StatusResponse.objects.filter(
                    response_order=response_order).last()
                if response_statuses is not None:
                    if response_statuses.status != 'Cancelled':
                        responses.append(response_order)

        if request.user.role == 'Supplier' or not request.user.role:
            for response_order in response_orders:
                response_statuses = StatusResponse.objects.filter(
                    response_order=response_order).last()
                response_order.last_status = response_statuses.status
                if response_statuses.status == 'Cancelled' \
                        or response_statuses.status == 'Approved' \
                        or response_statuses.status == 'Not Approved':
                    not_active_responses_order_users_id.append(response_statuses.response_order.response_user_id)
                    if request.user.id == response_order.response_user_id or not request.user.role:
                        responses.append(response_order)
                    else:
                        continue
                else:
                    responses.append(response_order)

        # if len(response_statuses) != 0:
        # 	responses.append(response_order)
        # 	if StatusResponse.objects.filter(response_order=response_order, status='Approved').first():
        # 		approved_response = response_order
        # 	if StatusResponse.objects.filter(response_order=response_order, status='Cancelled').first():
        # 		cancelled_response = response_order

        categories = CategoryOrder.objects.select_related().exclude(id=order.category_id)

        forms = None
        response_id = None
        error = request.GET.get('error')
        cancelled_response = request.GET.get('cancelled_response')
        if error == 'Approved':
            error = 'Заказ имеет статус Поставщик найден'
        elif error == 'Cancelled' or cancelled_response:  # error == 'Cancelled' or response_statuses.status == 'Cancelled':
            error = 'Ваш отклик отклонен'
        else:
            error = 'Заказ имеет статус отменён'

        if request.user.role == 'Supplier':
            forms = self.get_forms()
            response_id = response_orders.filter(
                response_user=request.user).values('id')
            if response_id:
                response_id = response_id[0]['id']
            else:
                response_id = None

        context = {
            'no_approved_response': no_approved_response,
            'approved_response': approved_response,
            'cancellation_not_available': True if request.GET.get('denied_cancellation') else False,
            'editing_not_available': True if request.GET.get('denied_editing') else False,
            'error': error,
            'order': order,
            'response_orders': responses,  # responses, #response_orders,
            'categories': categories,
            'forms': forms,
            'response_id': response_id,
            'response_order_user_id': self.request.user.id,
            'not_active_responses_order_users_id': not_active_responses_order_users_id

        }
        return render(request, self.template_name, context=context)

    def forms_valid(self, forms):
        user = self.request.user
        order = Order.objects.get(id=self.kwargs.get('pk'))

        if user.role == 'Supplier':
            response_order_form = forms.get('response_order')
            response = ResponseOrder.objects.create(order=order,
                                                    response_user=user,
                                                    price=response_order_form.data.get(
                                                        'price'),
                                                    offer=response_order_form.data.get(
                                                        'offer')
                                                    )

            response.save()

        return HttpResponseRedirect(self.request.path_info)

    def get_objects(self):
        user = self.request.user
        order = Order.objects.get(id=self.kwargs.get('pk'))

        if user.role == 'Supplier':
            response = ResponseOrder.objects.filter(
                order=order, response_user=user).first()

            return {'response_order': response}

    def order_confirmation(self, response_pk, order_pk):
        """Утверждение отклика и изменение статуса заказа на Not Active"""
        if self.POST:
            try:
                # status_response = StatusResponse.objects.filter(
                #     response_order_id=response_pk).last()
                #
                # status_response.status = 'Approved'
                # status_response.save()
                StatusResponse.objects.create(response_order_id=response_pk,
                                              status='Approved',
                                              user_initiator=self.user)
                order = get_object_or_404(Order, id=order_pk)
                order.status = 'Not Active'
                order.save()
            except Http404:
                pass
            return redirect(reverse_lazy('main'))

    # return redirect(reverse_lazy('orders:view_order', kwargs={'pk': order_pk}))

    def order_rejection(self, response_pk, order_pk):
        """
            Отклонение отклика Заказчиком.
            Для Администратора переключение статуса отклика кнопкой "Х" и возможность подтвердить отклик.

        """
        if self.POST:
            # Изменение статусов откликов для Админа
            if self.user.is_staff or self.user.is_ssuperuser:
                response_order_last = StatusResponse.objects.filter(response_order_id=response_pk).last()
                if response_order_last.status == 'Cancelled':
                    StatusResponse.objects.create(response_order_id=response_pk,
                                                  status='On Approval',
                                                  user_initiator=self.user)
                elif response_order_last.status == 'Approved':
                    pass
                else:
                    StatusResponse.objects.create(response_order_id=response_pk,
                                                  status='Cancelled',
                                                  user_initiator=self.user)

            else:
                # Отклнение откликов для Заказчика
                try:
                    # statuse_response = get_object_or_404(
                    #     StatusResponse, id=response_pk)
                    # statuse_response.status = 'Not Approved'
                    # statuse_response.save()
                    StatusResponse.objects.create(response_order_id=response_pk,
                                                  status='Cancelled',
                                                  user_initiator=self.user)
                    order = get_object_or_404(Order, id=order_pk)
                    order.status = 'Active'
                    order.save()
                except Http404:
                    pass

        return redirect(reverse_lazy('orders:view_order', kwargs={'pk': order_pk}))


class OrderBoardView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Order
    context_object_name = 'all_orders'
    template_name = 'orders/order_board.html'
    paginate_by = 2

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['all_category'] = CategoryOrder.objects.filter(is_active=True)
        return context

    def test_func(self):
        return self.request.user.role != 'Customer'


@login_required
@user_passes_test(order_board_check)
def table_order(request):
    """Обработчик доски заказов"""
    if 'pk' in request.GET:
        order = Order.objects.get(id=request.GET['pk'])
        order.delete()
    context = {}
    if request.user.role != 'Supplier':
        context['filtered_table'] = OrderFilter(
            request.GET, queryset=Order.objects.all())
    else:
        context['filtered_table'] = OrderFilter(
            request.GET, queryset=Order.objects.filter(status='Active'))
    # ! Здесь устанавливается пагинация
    paginated = Paginator(context['filtered_table'].qs, 2)
    page_number = request.GET.get('page')
    context['page_obj'] = paginated.get_page(page_number)

    return render(request, 'orders/order_board.html', context=context)


class DeleteCategory(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = CategoryOrder
    success_url = reverse_lazy('orders:categories')

    def test_func(self):
        return self.request.user.is_superuser or self.request.user.is_staff


@login_required
def categories(request):
    context = {}
    active_categories = CategoryOrder.objects.select_related() \
        .filter(is_active=True) \
        .annotate(count_orders=Count('order__responseorder__response_user_id',
                                     filter=Q(
                                         order__responseorder__statusresponse__status='Approved'),
                                     distinct=True)) \
        .values('id', 'name', 'image', 'description', 'count_orders')
    all_categories = CategoryOrder.objects.select_related() \
        .annotate(count_orders=Count('order__responseorder__response_user_id',
                                     filter=Q(
                                         order__responseorder__statusresponse__status='Approved'),
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


class DeleteOrder(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Класс-обработчик для удаления заказа"""
    model = Order

    def get_success_url(self):
        order_id = self.kwargs['pk']
        return reverse_lazy('orders:view_order', kwargs={'pk': order_id})

    def form_valid(self, form):
        order = self.get_object()
        if len(StatusResponse.objects.filter(response_order__order=order, status='Approved')) == 0:
            no_approved_response = True
        else:
            no_approved_response = False

        if (order.author == self.request.user and (order.status == 'Active' or no_approved_response)) \
                or self.request.user.is_superuser or self.request.user.is_staff:
            order.delete()
            return HttpResponseRedirect(self.get_success_url())
        else:
            if (order.author == self.request.user and (order.status == 'Not Active')):
                order.delete()
                return HttpResponseRedirect(self.get_success_url())
            return HttpResponseRedirect(f'{self.get_success_url()}?denied_cancellation=True')

    def test_func(self):
        order_id = self.kwargs['pk']
        order = get_object_or_404(Order, id=order_id)
        user_is_author = order.author == self.request.user

        return self.request.user.is_superuser or self.request.user.is_staff or user_is_author


class UpdateOrder(UpdateView):
    """Класс-обработчик для редактирования заказа"""
    model = Order
    template_name = 'orders/view_order.html'
    fields = [
        "name",
        "category",
        "end_time",
        "description"
    ]

    def get_success_url(self):
        order_id = self.kwargs['pk']
        return reverse_lazy('orders:view_order', kwargs={'pk': order_id})

    def form_valid(self, form):
        order = Order.objects.get(id=self.kwargs.get('pk'))

        if len(StatusResponse.objects.filter(response_order__order=order, status__in=['Approved', 'On Approval'])) == 0:
            no_responses = True
        else:
            no_responses = False

        if (order.author == self.request.user and no_responses) \
                or self.request.user.is_superuser or self.request.user.is_staff:
            form.save()

            return super().form_valid(form)
        else:
            return HttpResponseRedirect(f'{self.get_success_url()}?denied_editing=True')


class DeleteResponse(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Отклонение отклика Поставщиком"""
    model = ResponseOrder

    def get_success_url(self, page):
        return reverse_lazy('orders:view_order', args=[str(page)])

    def form_valid(self, form):
        response_object = self.get_object()
        if StatusResponse.objects.filter(
                Q(response_order_id=response_object.id) & Q(status='Approved')):
            no_approved_response = False
            cancelled_response = False
        elif StatusResponse.objects.filter(
                Q(response_order_id=response_object.id) & Q(status='Cancelled')):
            no_approved_response = True
            cancelled_response = True

        else:
            no_approved_response = True
            cancelled_response = False
        status = Order.objects.get(id=response_object.order_id)
        page = response_object.order_id

        if ((response_object.response_user_id == self.request.user.id) and (
                status.status == 'Active' or no_approved_response) and not cancelled_response):
            """Если нужно удалять отклики из БД"""
            # 	response_object.delete()
            # 	return HttpResponseRedirect(self.get_success_url(page))
            #
            # return HttpResponseRedirect(
            # 	f'{self.get_success_url(page)}?denied_cancellation=True&cancelled_response={cancelled_response}')
            """Если нужно установить статус 'Cancelled' для отклика в БД"""
            try:

                StatusResponse.objects.create(response_order_id=self.object.pk,
                                              status='Cancelled',
                                              user_initiator=response_object.response_user)
            except Http404:
                pass

        return HttpResponseRedirect(f'{self.get_success_url(page)}')

    def test_func(self):
        order_id = self.kwargs['pk']
        order = get_object_or_404(Order, id=order_id)
        user_is_author = order.author == self.request.user

        return self.request.user.is_superuser or self.request.user.is_staff or user_is_author


class UpdateResponse(LoginRequiredMixin, UpdateView):
    model = ResponseOrder
    template_name = 'orders/view_order.html'
    fields = ['offer', 'price']

    def get_success_url(self, page):
        return reverse_lazy('orders:view_order', args=[str(page), ])

    def form_valid(self, form):
        response_order = ResponseOrder.objects.get(id=self.kwargs.get('pk'))
        status_order = Order.objects.filter(id=response_order.order_id).first()
        status_response = StatusResponse.objects.filter(
            Q(response_order_id=response_order.id)).last()
        page = response_order.order_id

        if status_order.status != 'Active':

            return HttpResponseRedirect(f'{self.get_success_url(page)}?denied_editing=True&error=Active')
        elif status_response.status == 'Approved':

            return HttpResponseRedirect(f'{self.get_success_url(page)}?denied_editing=True&error=Approved')
        elif status_response.status == 'Cancelled':

            return HttpResponseRedirect(f'{self.get_success_url(page)}?denied_editing=True&error=Cancelled')
        else:
            no_responses = True

        if (response_order.response_user_id == self.request.user.id and no_responses):
            form.save()
            return HttpResponseRedirect(self.get_success_url(page))
