from django.shortcuts import render

# Create your views here.
from django.views import View

from orders.models import CategoryOrder


class MainView(View):
    template_name = 'orders/main.html'
    title = 'Главная'

    def get(self, request, *args, **kwargs):
        content = {
            'title': self.title,
            'categories': CategoryOrder.objects.all().order_by('-id')[:6]
        }

        return render(request, self.template_name, content)
