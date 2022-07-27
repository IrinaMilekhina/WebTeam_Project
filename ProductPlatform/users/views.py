from datetime import datetime

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView, LogoutView, PasswordResetView, PasswordResetDoneView, \
    PasswordResetConfirmView, PasswordResetCompleteView
from django.contrib import messages
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Count
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import ListView, UpdateView, DetailView
from django.views.generic.edit import FormView

from orders.models import ResponseOrder, Order, StatusResponse
from users.forms import PersonalAccountEditForm
from users.forms import UserLoginForm, UserRegisterForm
from users.models import Profile


class PersonalAccountListView(LoginRequiredMixin, ListView):
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


class PersonalAccountEditView(LoginRequiredMixin, UpdateView):
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

    def get(self, request, *args, **kwargs):
        return redirect(reverse_lazy('main'))


class PersonalActiveOrdersView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Order
    template_name = 'users/account_active_orders.html'
    context_object_name = 'orders'
    paginate_by = 3

    def get_context_data(self, *, object_list=None, **kwargs):
        """Метод для создания необходимого контекста для активных заказов личного кабинета"""
        context = super().get_context_data(**kwargs)
        user = self.request.user
        page = self.request.GET.get('page')
        
        # для Заказчика
        if user.role == 'Customer':
            response_for_customer = ResponseOrder.objects.filter(order__author=user.pk)
            active_orders = Order.objects.select_related()\
                .filter(end_time__gte=datetime.today(), author_id=user.pk)\
                .annotate(count_response=Count('responseorder')) \
                .values('id', 'category__name', 'author__city', 'name', 'description',
                        'status', 'create_at', 'end_time', 'count_response')

            paginator = Paginator(active_orders, per_page=3)
            try:
                orders_paginator = paginator.page(page)
            except PageNotAnInteger:
                orders_paginator = paginator.page(1)
            except EmptyPage:
                orders_paginator = paginator.page(paginator.num_pages)
            context['paginator'] = orders_paginator.paginator
            context['page_obj'] = orders_paginator
            context['responses_to_orders'] = response_for_customer

            return context

        # для поставщика
        elif user.role == 'Supplier':
            active_responses = []
            responses = ResponseOrder.objects.filter(response_user=user, order__end_time__gte=datetime.today())

            for response in responses:
                statuses = StatusResponse.objects.filter(
                    response_order=response,
                    status__in=['Not Approved', 'Cancelled'])
                if len(statuses) == 0:
                    if StatusResponse.objects.filter(response_order=response, status='Approved').first():
                        active_responses.append({'response': response, 'status': 'Утверждён'})
                    else:
                        active_responses.append({'response': response, 'status': 'На утверждении'})
            
            paginator = Paginator(active_responses, per_page=3)
            try:
                orders_paginator = paginator.page(page)
            except PageNotAnInteger:
                orders_paginator = paginator.page(1)
            except EmptyPage:
                orders_paginator = paginator.page(paginator.num_pages)
            context['paginator'] = orders_paginator.paginator
            context['page_obj'] = orders_paginator
            
            return context

    def test_func(self):
        return not self.request.user.is_superuser and not self.request.user.is_staff


class PersonalHistoryOrdersView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Order
    template_name = 'users/account_history_orders.html'
    context_object_name = 'orders'
    paginate_by = 3

    def get_context_data(self, *, object_list=None, **kwargs):
        """Метод для создания необходимого контекста для истории заказов личного кабинета"""
        context = super(PersonalHistoryOrdersView,
                        self).get_context_data(**kwargs)
        current_profile = Profile.objects.get(pk=self.request.user.pk)
        responses, orders, status_responses = None, None, None
        if current_profile.role == 'Customer':
            responses = ResponseOrder.objects.filter(order__author=self.request.user.pk, order__status='Not Active')
            orders = Order.objects.filter(author=self.request.user.pk, status='Not Active')
            status_responses = StatusResponse.objects.filter(response_order__order__author=self.request.user.pk,
                                                             response_order__order__status='Not Active')
        elif current_profile.role == 'Supplier':
            orders = Order.objects.filter(responseorder__response_user=self.request.user.pk, status='Not Active')
            responses = ResponseOrder.objects.filter(order__id__in=orders.values_list('id'), order__status='Not Active')
            status_responses = StatusResponse.objects.filter(response_order__order__id__in=orders.values_list('id'),
                                                             response_order__order__status='Not Active')
        history_orders = []
        for item in orders:
            response_count = responses.filter(order=item.id).count()
            approved_response_user_id = None
            try:
                approved_response = status_responses.get(status='Approved', response_order__order=item.id)
                if current_profile.role == 'Supplier' \
                        and approved_response.response_order.response_user.id == current_profile.id:
                    status = 'Ваш отклик утвержден'
                else:
                    status = 'Поставщик утвержден'
                approved_response_user_id = approved_response.response_order
            except Exception:
                status = 'Отменен'
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
                'response_approved': approved_response_user_id
            })
        page = self.request.GET.get('page')
        paginator = Paginator(history_orders, per_page=3)
        try:
            orders_paginator = paginator.page(page)
        except PageNotAnInteger:
            orders_paginator = paginator.page(1)
        except EmptyPage:
            orders_paginator = paginator.page(paginator.num_pages)
        context['paginator'] = orders_paginator.paginator
        context['page_obj'] = orders_paginator
        context['user'] = current_profile
        return context

    def test_func(self):
        return not self.request.user.is_superuser and not self.request.user.is_staff


class ProfilePasswordResetView(PasswordResetView):
    title = "Сброс пароля"
    subject_template_name = "users/registration/password_reset_subject.txt"
    email_template_name = "users/registration/password_reset_email.html"
    template_name = "users/registration/password_reset_form.html"
    success_url = reverse_lazy("users:password_reset_done")

    def form_valid(self, form):
        try:
            user = Profile.objects.get(email=form.cleaned_data['email'])
            if user:
                return super().form_valid(form)
        except Profile.DoesNotExist:
            form.errors['InvalidEmail'] = 'Введен некорректный email. Введите email, указанный при регистрации.'
            return super().form_invalid(form)


class ProfilePasswordResetDoneView(PasswordResetDoneView):
    title = "Сброс пароля"
    template_name = "users/registration/password_reset_done.html"


class ProfilePasswordResetConfirmView(PasswordResetConfirmView):
    title = "Сброс пароля"
    template_name = "users/registration/password_reset_confirm.html"
    success_url = reverse_lazy("users:password_reset_complete")


class ProfilePasswordResetCompleteView(PasswordResetCompleteView):
    title = "Сброс пароля"
    template_name = "users/registration/password_reset_complete.html"


class ProfileView(LoginRequiredMixin, DetailView):
    """Класс-обработчик для отображения выбранного профиля"""
    model = Profile
    template_name = 'users/profile.html'

    def get(self, request, *args, **kwargs):
        """Если приходит GET запрос, получаем профиль по id и рендерим шаблон users/profile.html"""
        try:
            if kwargs.get('id'):
                profile_id = kwargs['id']
                user_profile = get_object_or_404(Profile, id=profile_id)
                if user_profile.role == 'Customer':
                    orders_amount = len(Order.objects.filter(author=user_profile.id))

                    return render(request, self.template_name,
                                  {'profile': user_profile, 'orders_amount': orders_amount})
                elif user_profile.role == 'Supplier':
                    responses_amount = len(ResponseOrder.objects.filter(response_user_id=user_profile.id))

                    return render(request, self.template_name,
                                  {'profile': user_profile, 'responses_amount': responses_amount})

            return render(request, self.template_name, {'ERROR': 'Страница не найдена', 'title': '404'})
        except Http404:
            return render(request, self.template_name, {'ERROR': 'Страница не найдена', 'title': '404'})

