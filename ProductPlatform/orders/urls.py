"""orders URL Configuration

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
from .views import Category, CreateOrder, OrderView, table_order, DeleteCategory, categories, DeleteOrder,UpdateOrder, DeleteResponse, UpdateResponse

app_name = 'orders'

urlpatterns = [
    path('categories/', categories, name='categories'),
    path('category/<int:id>', Category.as_view(), name='category'),
    path('create_order/', CreateOrder.as_view(), name='create_order'),
    path('view_order/<int:pk>/', OrderView.as_view(), name='view_order'),
    path("table_order/", table_order, name="table_order"),
    path('category/delete/<int:pk>/', DeleteCategory.as_view(), name='delete_category'),
    path('order_delete/<int:pk>/', DeleteOrder.as_view(), name='delete_order'),
    path('update/<int:pk>/', UpdateOrder.as_view(), name='update_order'),
    path('response_delete/<int:pk>/',
         DeleteResponse.as_view(), name='delete_response'),
    path('response_update/<int:pk>/',
         UpdateResponse.as_view(), name='response_update'),
    path('order_confirmation/<int:response_pk>/<int:order_pk>/', OrderView.order_confirmation,
         name='order_confirmation'),
    path('order_rejection/<int:response_pk>/<int:order_pk>/',
         OrderView.order_rejection, name='order_rejection'),
    


]
