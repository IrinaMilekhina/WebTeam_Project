from django.contrib import admin

from .models import Order, CategoryOrder, ResponseOrder, StatusResponse, Feedback


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


class AdminStatusResponse(admin.ModelAdmin):
    list_display = ['id', 'status', 'time_status', 'response_order', 'user_initiator']
    list_filter = ['status', 'time_status']
    search_fields = ['status', 'time_status', 'response_order', 'user_initiator']


class AdminFeedback(admin.ModelAdmin):
    list_display = ['id', 'name_user', 'issue']
    list_display_links = ['name_user']

admin.site.register(Order, AdminOrders)
admin.site.register(CategoryOrder, AdminCategory)
admin.site.register(ResponseOrder, AdminResponse)
admin.site.register(StatusResponse, AdminStatusResponse)
admin.site.register(Feedback, AdminFeedback)
