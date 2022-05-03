import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views import View
from .models import User

# Create your views here.
def index(request):
    if User.objects.count() == 0:
        param = {}
    else:
        users = User.objects.filter(role="Исполнитель")
        for user in users:
            user.phone = '+'+str(user.phone) if user.phone != '-' else '-'
        cities = User.objects.all().values_list('city').distinct()
        param = {'specialists': users,
                 'cities': cities}
    return render(request, 'main/list.html', param)
