from django.urls import path, re_path, include
from . import views

urlpatterns = [
    path('', views.index, name = 'index'),
    path('user-filter', views.user_filter, name = 'user-filter'),
    path('bot/', include('tgbot.urls')),
]
