from django.contrib import admin

from .models import User, Vacancy, Message, Info, Specialisation

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("chat_id", "user", "name", "phone", "city")
    list_filter = ("city", )

@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    list_display = ("chat_id", "text", "date", "city")
    list_filter = ("chat_id", "city")

@admin.register(Info)
class InfoAdmin(admin.ModelAdmin):
    list_display = ("clue", "text")

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("clue", "text")

@admin.register(Specialisation)
class SpecialityAdmin(admin.ModelAdmin):
    list_display = ("clue", "name")
