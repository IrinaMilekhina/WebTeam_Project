from django.shortcuts import render

# Create your views here.
from django.views import View


class MainView(View):
    template_name = 'users/base.html'
    title = 'Главная'

    def get(self, request, *args, **kwargs):
        content = {
            'title': self.title,
        }

        return render(request, self.template_name, content)
