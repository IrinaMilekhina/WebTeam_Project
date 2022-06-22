from django.contrib import admin

from .models import Order, CategoryOrder, ResponseOrder


class AdminOrders(admin.ModelAdmin):
    list_display = ['author', 'category', 'name', 'status', ]
    list_filter = ['category', 'status']
    search_fields = ['category', 'name', 'author']


class AdminCategory(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'description', 'image']
    list_filter = ['name']
    search_fields = ['name']


class AdminResponse(admin.ModelAdmin):
    list_display = ['order', 'response_user', 'price']
    list_filter = ['order', 'response_user', 'price']
    search_fields = ['order', 'response_user', 'price']


admin.site.register(Order, AdminOrders)
admin.site.register(CategoryOrder, AdminCategory)
admin.site.register(ResponseOrder, AdminResponse)
