from django.contrib.auth.views import LoginView, LogoutView
from django.contrib import messages
from django.views.generic.edit import FormView

from orders.models import ResponseOrder, Order
from users.forms import UserLoginForm, UserRegisterForm
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, UpdateView
from django.urls import reverse_lazy

from users.forms import PersonalAccountEditForm
from users.models import Profile


class PersonalAccountListView(ListView):
    """Класс-обработчик для отображения информации в личном кабинете"""
    title = 'Личный кабинет'
    model = Profile
    template_name = 'users/personal_account.html'
    context_object_name = 'account'

    def get_context_data(self, *, object_list=None, **kwargs):
        """Метод для создания необходимого контекста для личного кабинета"""
        context = super(PersonalAccountListView,
                        self).get_context_data(**kwargs)
        context['account'] = Profile.objects.get(pk=self.request.user.pk)
        context['title'] = self.title
        return context


class PersonalAccountEditView(UpdateView):
    """Класс-обработчик для редактирования информации в личном кабинете"""
    model = Profile
    template_name = 'users/personal_account_edit.html'
    form_class = PersonalAccountEditForm
    success_url = reverse_lazy('users:account_edit')

    def get_object(self, queryset=None):
        """Метод для получения объекта для использования"""
        return get_object_or_404(Profile, pk=self.request.user.pk)

    def get_context_data(self, *, object_list=None, **kwargs):
        """Метод для создания необходимого контекста для личного кабинета"""
        context = super(PersonalAccountEditView,
                        self).get_context_data(**kwargs)
        context['user'] = Profile.objects.get(pk=self.request.user.pk)
        return context

    def post(self, request, *args, **kwargs):
        form = self.form_class(data=request.POST, instance=self.request.user)
        if form.is_valid():
            form.save()
            return redirect(self.success_url)
        return redirect(self.success_url)


class LoginListView(LoginView):
    template_name = 'users/login.html'
    form_class = UserLoginForm
    title = 'Авторизация'


class RegisterListView(FormView):
    model = Profile
    template_name = 'users/registration.html'
    form_class = UserRegisterForm
    success_url = reverse_lazy('users:login')
    title = 'Регистрация'

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def form_invalid(self, form):
        print(form.errors)
        return super().form_invalid(form)


class Logout(LogoutView):
    template_name = 'orders/main.html'


class PersonalActiveOrdersView(ListView):
    model = Order
    template_name = 'users/account_active_orders.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        """Метод для создания необходимого контекста для активных заказов личного кабинета"""
        context = super(PersonalActiveOrdersView,
                        self).get_context_data(**kwargs)
        current_profile = Profile.objects.get(pk=self.request.user.pk)
        responses, orders = None, None
        if current_profile.role == 'Customer':
            responses = ResponseOrder.objects.filter(order__author=self.request.user.pk, order__status=True)
            orders = Order.objects.filter(author=self.request.user.pk, status=True)
        elif current_profile.role == 'Supplier':
            orders = Order.objects.filter(responseorder__response_user=self.request.user.pk, status=True)
            responses = ResponseOrder.objects.filter(order__id__in=orders.values_list('id'), order__status=True)
        active_orders = []
        for item in orders:
            response_count = responses.filter(order=item.id).count()
            status = 'Поиск заказчика'
            response_approved = None
            for response in responses.filter(order=item.id):
                if 'Approved' == response.status:
                    if current_profile.role == 'Supplier' and response.response_user.id == current_profile.id:
                        status = 'Ваш отклик утвержден'
                    else:
                        status = 'Заказчик утвержден'
                    response_approved = response
            active_orders.append({
                'name': item.name,
                'order_num': item.id,
                'description': item.description,
                'category': item.category.name,
                'city': item.author.city,
                'date_to': item.end_time.date(),
                'response_count': response_count,
                'status': status,
                'response_approved': response_approved
            })
        context['orders'] = active_orders
        context['user'] = current_profile
        return context


class PersonalHistoryOrdersView(ListView):
    model = Order
    template_name = 'users/account_history_orders.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        """Метод для создания необходимого контекста для истории заказов личного кабинета"""
        context = super(PersonalHistoryOrdersView,
                        self).get_context_data(**kwargs)
        current_profile = Profile.objects.get(pk=self.request.user.pk)
        responses, orders = None, None
        if current_profile.role == 'Customer':
            responses = ResponseOrder.objects.filter(order__author=self.request.user.pk, order__status=False)
            orders = Order.objects.filter(author=self.request.user.pk, status=False)
        elif current_profile.role == 'Supplier':
            orders = Order.objects.filter(responseorder__response_user=self.request.user.pk, status=False)
            responses = ResponseOrder.objects.filter(order__id__in=orders.values_list('id'), order__status=False)
        history_orders = []
        for item in orders:
            response_count = responses.filter(order=item.id).count()
            status = 'Отменен'
            response_approved = None
            for response in responses.filter(order=item.id):
                if 'Approved' == response.status:
                    if current_profile.role == 'Supplier' and response.response_user.id == current_profile.id:
                        status = 'Ваш отклик утвержден'
                    else:
                        status = 'Заказчик утвержден'
                    response_approved = response
            history_orders.append({
                'name': item.name,
                'author': item.author,
                'order_num': item.id,
                'description': item.description,
                'category': item.category.name,
                'city': item.author.city,
                'date_to': item.end_time.date(),
                'response_count': response_count,
                'status': status,
                'response_approved': response_approved
            })
        context['orders'] = history_orders
        context['user'] = current_profile
        return context
