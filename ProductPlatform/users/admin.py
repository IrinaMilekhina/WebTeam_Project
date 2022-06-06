from django.contrib import admin
from .models import Profile

from .models import Profile


# Register your models here.


class UserProfile(admin.ModelAdmin):
    list_display = ['username', 'comp_name', 'phone_number', 'email']
    list_display_links = ['username']
    list_filter = ['role']
    search_fields = ['comp_name']


admin.site.register(Profile, UserProfile)
