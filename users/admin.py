from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'username', 'full_name', 'user_type', 'payment_made',
                    'last_payment', 'plan')
    search_fields = ('email', 'username', 'first_name', 'last_name', 'payment_made',
                     'last_payment', 'plan')
    list_filter = ('user_type', 'payment_made', 'last_payment', 'plan')

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'username')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Additional info', {'fields': ('user_type', 'payment_made', 'last_payment', 'plan')}),
    )

    readonly_fields = ('date_joined', 'last_login')

    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"

    full_name.short_description = 'Full Name'
    full_name.admin_order_field = 'first_name'


admin.site.register(User, CustomUserAdmin)
