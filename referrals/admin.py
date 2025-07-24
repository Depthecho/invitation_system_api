from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('phone', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Referral info', {'fields': ('invite_code', 'activated_invite')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone', 'password1', 'password2'),
        }),
    )
    list_display = ('phone', 'invite_code', 'activated_invite')
    search_fields = ('phone', 'invite_code')
    ordering = ('phone',)

admin.site.register(User, CustomUserAdmin)