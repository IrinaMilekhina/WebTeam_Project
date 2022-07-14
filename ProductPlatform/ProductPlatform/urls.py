"""ProductPlatform URL Configuration

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
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from ProductPlatform.script.change_order_status import start_thread_check_order_status
from orders.views import MainView

start_thread_check_order_status()  # запуск скрипта проверки заказов на актуальность по дате

urlpatterns = [
    path('', MainView.as_view(), name='main'),
    path('admin/', admin.site.urls),
    path('orders/', include('orders.urls', namespace='orders')),
    path('users/', include('users.urls', namespace='users')),
    path('users/', include('django.contrib.auth.urls'))
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
