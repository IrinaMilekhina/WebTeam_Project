from django.contrib import admin

from .models import Order, CategoryOrder, ResponseOrder, StatusResponse


class AdminOrders(admin.ModelAdmin):
    list_display = ['author', 'category', 'name', 'status', ]
    list_filter = ['category', 'status']
    search_fields = ['category', 'name', 'author']


class AdminCategory(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'description', 'image']
    list_filter = ['name']
    search_fields = ['name']


class AdminResponse(admin.ModelAdmin):
    list_display = ['order', 'response_user']
    list_filter = ['order', 'response_user']
    search_fields = ['order', 'response_user']


class AdminStatusResponse(admin.ModelAdmin):
    list_display = ['id', 'status', 'time_status', 'response_order', 'user_initiator']
    list_filter = ['status', 'time_status']
    search_fields = ['status', 'time_status', 'response_order', 'user_initiator']

admin.site.register(Order, AdminOrders)
admin.site.register(CategoryOrder, AdminCategory)
admin.site.register(ResponseOrder, AdminResponse)
admin.site.register(StatusResponse, AdminStatusResponse)
