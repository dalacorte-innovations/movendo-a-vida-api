from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'username', 'full_name', 'user_type', 'payment_made', 'user_free',
                    'last_payment', 'restricted_access', 'registration_date')
    search_fields = ('email', 'username', 'first_name', 'last_name', 'payment_made', 'user_free',
                     'last_payment', 'restricted_access', 'registration_date')
    list_filter = ('user_type', 'payment_made', 'user_free', 'last_payment', 'restricted_access',
                   'registration_date')

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'username', 'telephone')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Additional info', {'fields': ('user_type', 'payment_made', 'user_free', 'last_payment',
                                        'restricted_access', 'registration_date')}),
    )

    readonly_fields = ('date_joined', 'last_login', 'registration_date')

    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"

    full_name.short_description = 'Full Name'
    full_name.admin_order_field = 'first_name'


admin.site.register(User, CustomUserAdmin)
