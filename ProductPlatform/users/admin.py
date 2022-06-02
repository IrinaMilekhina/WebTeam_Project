from django.contrib import admin

# Register your models here.

class UserProfile(admin.ModelAdmin):
    list_display = ['comp_name', 'phone_number', 'email']
    list_filter = ['role']
    search_fields = ['comp_name']


admin.site.register(Profile, UserProfile)