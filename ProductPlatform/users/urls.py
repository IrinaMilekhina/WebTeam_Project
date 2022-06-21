"""users URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from .views import LoginListView, RegisterListView, Logout, PersonalActiveOrdersView, PersonalHistoryOrdersView

from users.views import PersonalAccountListView, PersonalAccountEditView

app_name = 'users'

urlpatterns = [
    path('account/', PersonalAccountListView.as_view(), name='account'),
    path('account_edit/', PersonalAccountEditView.as_view(), name='account_edit'),
    path('login/', LoginListView.as_view(), name='login'),
    path('register/', RegisterListView.as_view(), name='register'),
    path('logout/', Logout.as_view(), name='logout'),
    path('account_history_orders/', PersonalHistoryOrdersView.as_view(), name='account_active_orders'),
    path('account_active_orders/', PersonalActiveOrdersView.as_view(), name='account_active_orders'),
]
