from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, UserReferral, WithdrawalRequest

class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'username', 'first_name', 'phone', 'user_type', 'payment_made',
                    'last_payment', 'plan', 'referral_code', 'pix_key',
                    'terms_accepted', 'privacy_accepted')
    search_fields = ('email', 'username', 'first_name', 'last_name', 'phone', 'payment_made',
                     'last_payment', 'plan', 'referral_code')
    list_filter = ('user_type', 'payment_made', 'last_payment', 'plan',
                  'terms_accepted', 'privacy_accepted')

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'phone', 'image', 'username', 'referral_code', 'pix_key')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Additional info', {'fields': ('user_type', 'payment_made', 'last_payment', 'plan', 'stripe_customer_id')}),
        ('Terms & Privacy', {'fields': ('terms_accepted', 'terms_accepted_date', 'privacy_accepted', 'privacy_accepted_date')}),
    )

    readonly_fields = ('date_joined', 'last_login', 'terms_accepted_date', 'privacy_accepted_date')
    

class UserReferralAdmin(admin.ModelAdmin):
    list_display = ('referred_by', 'referred_user', 'timestamp')
    search_fields = ('referred_by__email', 'referred_user__email')
    list_filter = ('timestamp',)

    def referred_by(self, obj):
        return obj.referred_by.email

    def referred_user(self, obj):
        return obj.referred_user.email

class WithdrawalRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'request_date', 'status')
    search_fields = ('user__email', 'amount', 'status')
    list_filter = ('status', 'request_date')

    def user(self, obj):
        return obj.user.email

admin.site.register(User, CustomUserAdmin)
admin.site.register(UserReferral, UserReferralAdmin)
admin.site.register(WithdrawalRequest, WithdrawalRequestAdmin)