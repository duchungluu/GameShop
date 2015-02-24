from django.contrib import admin
from game.models import *

from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'isDeveloper', 'regDate')


class StoreGameAdmin(admin.ModelAdmin):
    list_display = ('title', 'id', 'author', 'relDate', 'price', 'genre')


class UserGameAdmin(admin.ModelAdmin):
    list_display = ('game', 'owner', 'purDate', 'rating')


class GameScoreAdmin(admin.ModelAdmin):
    list_display = ('game', 'player', 'score')


class GameGenreAdmin(admin.ModelAdmin):
    list_display = ('genre', 'desc')


class GameSaveAdmin(admin.ModelAdmin):
    list_display = ('game', 'user', 'saveData', 'saveDate')

admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(StoreGame, StoreGameAdmin)
admin.site.register(UserGame, UserGameAdmin)
admin.site.register(GameScore, GameScoreAdmin)
admin.site.register(GameGenre, GameGenreAdmin)
admin.site.register(GameSave, GameSaveAdmin)

#This is used to customize User view in Admin
UserAdmin.list_display = ('username', 'email', 'first_name', 'last_name', 'is_active', 'date_joined', 'is_staff')
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
