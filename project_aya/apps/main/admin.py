from django.contrib import admin

from .models import User, Vacancy, Message, Info, Specialisation, Words, DeleteMessage

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
class SpecialisationAdmin(admin.ModelAdmin):
    list_display = ("clue", "name")

@admin.register(Words)
class WordsAdmin(admin.ModelAdmin):
    list_display = ("clue", "word")

@admin.register(DeleteMessage)
class DeleteMessageAdmin(admin.ModelAdmin):
    list_display = ("chat_id", "msg_id", "msg_date", "delete_date", "deleted")
    list_filter = ("deleted", )
