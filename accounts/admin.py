from django.utils.translation import ugettext, ugettext_lazy as _
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.contrib.auth.models import User, Group
from django.contrib.sites.models import Site
from models import CustomUser

## cleanup unnecessary admins of original user ##
admin.site.unregister(User)
# admin.site.unregister(Group) # comment this if this is not used
admin.site.unregister(Site) # also unregister this to be clean

## add new admins in auth module ##
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'karma')
    fieldsets = None
admin.site.register(CustomUser, CustomUserAdmin)
