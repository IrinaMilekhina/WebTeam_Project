from django.contrib import admin
from .models import Orders, Category


class AdminOrders(admin.ModelAdmin):
    list_display = ['author', 'category', 'name', 'status', ]
    list_filter = ['category', 'status']
    search_fields = ['category', 'name', 'author']


class AdminCategory(admin.ModelAdmin):
    list_display = ['name']
    list_filter = ['name']
    search_fields = ['name']


admin.site.register(Orders, AdminOrders)
admin.site.register(Category, AdminCategory)

