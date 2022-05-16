import json
from django.shortcuts import render
from django.http import JsonResponse, HttpResponseBadRequest
from django.views import View
from .models import User, Specialisation

# Create your views here.
def index(request):
    if User.objects.count() == 0:
        param = {}
    else:
        users = User.objects.filter(role="Исполнитель").exclude(name=None)
        cities = User.objects.exclude(city=None).exclude(city='Неважно').values_list('city', flat=True).order_by('city').distinct()
        specialities = Specialisation.objects.order_by('name')
        params = {'specialists': get_users_array(users),
                 'cities': cities,
                 'specialities': specialities}
    return render(request, 'main/list.html', params)

def user_filter(request):
    if request.is_ajax and request.method == "GET":
        users = User.objects.filter(role="Исполнитель").exclude(name=None)
        city = request.GET.get("city", None)
        speciality = request.GET.get("speciality", None)
        experience = request.GET.get("experience", None)
        if city != None:
            users = users.filter(city=city)
            if speciality != None:
                users = users.filter(speciality=speciality)
            if experience != None:
                users = users.filter(experience=experience)
        else:
            if speciality != None:
                users = users.filter(speciality=speciality)
                if city != None:
                    users = users.filter(city=city)
                if experience != None:
                    users = users.filter(experience=experience)
            else:
                if experience != None:
                    users = users.filter(experience=experience)
                    if city != None:
                        users = users.filter(city=city)
                    if speciality != None:
                        users = users.filter(speciality=speciality)
        return render(request, 'main/user_list.html', {'specialists': get_users_array(users),})
        #return JsonResponse(users, status = 200)

def get_users_array(users):
    specialities = Specialisation.objects.order_by('name')
    users_arr = []
    for user in users:
        user.phone = '+'+str(user.phone) if user.phone != '-' else '-'
        tmp_arr = {
            'id': user.id,
            'role': user.role,
            'name': user.name,
            'city': user.city,
            'experience_clue': user.experience,
            'experience_desc': '',
            'phone': user.phone,
            'user': user.user,
            'description': user.description,
            'speciality_clue': user.speciality,
            'speciality_name': '',
            'photo_url': '',
            'class': ''
        }
        if user.experience == 'less-one':
            tmp_arr['experience_desc'] = 'Менее года'
        elif user.experience == 'one-three':
            tmp_arr['experience_desc'] = '1-3 года'
        elif user.experience == 'more-three':
            tmp_arr['experience_desc'] = 'Более 3 лет'
        for spec in specialities:
            if spec.clue == user.speciality: tmp_arr['speciality_name'] = spec
        if user.photo_url != '-':
            tmp_arr['photo_url'] = 'background-image: url("../static/img/user_photos/'+str(user.chat_id)+'.jpg");'
            tmp_arr['class'] = 'has-user-img'
        else:
            tmp_arr['class'] = 'no-user-img'
        users_arr.append(tmp_arr)
    return users_arr
