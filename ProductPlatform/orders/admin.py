from django.contrib import admin
from .models import Order, CategoryOrder


class AdminOrders(admin.ModelAdmin):
    list_display = ['author', 'category', 'name', 'status', ]
    list_filter = ['category', 'status']
    search_fields = ['category', 'name', 'author']


class AdminCategory(admin.ModelAdmin):
    list_display = ['name']
    list_filter = ['name']
    search_fields = ['name']


admin.site.register(Order, AdminOrders)
admin.site.register(CategoryOrder, AdminCategory)
