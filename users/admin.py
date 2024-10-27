from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, UserReferral

class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'username', 'first_name', 'phone', 'user_type', 'payment_made',
                    'last_payment', 'plan', 'referral_code')
    search_fields = ('email', 'username', 'first_name', 'last_name', 'phone', 'payment_made',
                     'last_payment', 'plan', 'referral_code')
    list_filter = ('user_type', 'payment_made', 'last_payment', 'plan')

    fieldsets = (
        (None, {'fields': ('email', 'password')}), 
        ('Personal info', {'fields': ('first_name', 'last_name', 'phone', 'image', 'username', 'referral_code')}), 
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}), 
        ('Important dates', {'fields': ('last_login', 'date_joined')}), 
        ('Additional info', {'fields': ('user_type', 'payment_made', 'last_payment', 'plan', 'stripe_customer_id')}), 
    )

    readonly_fields = ('date_joined', 'last_login')

class UserReferralAdmin(admin.ModelAdmin):
    list_display = ('referred_by', 'referred_user', 'timestamp')
    search_fields = ('referred_by__email', 'referred_user__email')
    list_filter = ('timestamp',)

    def referred_by(self, obj):
        return obj.referred_by.email

    def referred_user(self, obj):
        return obj.referred_user.email

admin.site.register(User, CustomUserAdmin)
admin.site.register(UserReferral, UserReferralAdmin)
