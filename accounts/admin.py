from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'middle_name', 'last_name', 'user_role', 'balance', 'is_active')
    list_filter = ('user_role', 'is_active')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('username', 'user_role')

    # Customize the admin view fieldsets
    fieldsets = (
        ('Login Information', {
            'fields': ('username', 'password')
        }),
        ('Personal Information', {
            'fields': ('first_name', 'middle_name', 'last_name', 'email')
        }),
        ('Role & Balance', {
            'fields': ('user_role', 'balance')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ('collapse',)
        }),
        ('Important Dates', {
            'fields': ('last_login', 'date_joined'),
            'classes': ('collapse',)
        }),
    )

    # Customize the add user form
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'first_name', 'middle_name',
                      'last_name', 'user_role', 'balance', 'is_active'),
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing an existing object
            return ('user_role', 'balance') + self.readonly_fields
        return self.readonly_fields

admin.site.register(CustomUser, CustomUserAdmin)
