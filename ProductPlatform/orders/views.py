from django.shortcuts import render
from django.views.generic import ListView
from orders.models import CategoryOrder
from django.views import View

class CategoryOrderView(ListView):
    model = CategoryOrder
    # смотря что будем выводить если все, то так, либо
    #queryset = CategoryOrder.objects.all()
    queryset = CategoryOrder.objects.filter(is_active=True)
    context_object_name = 'all_categories'
    template_name = 'orders/categories.html'
    paginate_by = 2  # заменить на нужное количество

class MainView(View):
    template_name = 'orders/main.html'
    title = 'Главная'

    def get(self, request, *args, **kwargs):
        content = {
            'title': self.title,
            'categories': CategoryOrder.objects.all().order_by('-id')[:6]
        }

        return render(request, self.template_name, content)

