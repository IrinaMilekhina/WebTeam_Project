from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.views.generic.edit import FormView
from users.forms import UserLoginForm, UserRegisterForm
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, UpdateView
from django.urls import reverse_lazy

from users.forms import PersonalAccountEditForm
from users.models import Profile


class PersonalAccountListView(ListView):
    """Класс-обработчик для отображения информации в личном кабинете"""
    model = Profile
    template_name = 'users/personal_account.html'
    context_object_name = 'account'

    def get_context_data(self, *, object_list=None, **kwargs):
        """Метод для создания необходимого контекста для личного кабинета"""
        context = super(PersonalAccountListView, self).get_context_data(**kwargs)
        context['account'] = Profile.objects.get(pk=self.request.user.pk)
        return context


class PersonalAccountEditView(UpdateView):
    """Класс-обработчик для редактирования информации в личном кабинете"""
    model = Profile
    template_name = 'users/personal_account_edit.html'
    form_class = PersonalAccountEditForm
    success_url = reverse_lazy('users:account')

    def get_object(self, queryset=None):
        """Метод для получения объекта для использования"""
        return get_object_or_404(Profile, pk=self.request.user.pk)

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
