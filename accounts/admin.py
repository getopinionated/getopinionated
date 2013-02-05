from django.contrib import admin
from models import UserProfile
from django.contrib.auth.admin import UserAdmin 
from django.contrib.auth.models import User

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', ]

admin.site.register(UserProfile, UserProfileAdmin)
