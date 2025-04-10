from django.contrib import admin
from .models import Plan, Subscription

@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'stripe_price_id', 'price', 'currency', 'interval')
    search_fields = ('name', 'stripe_price_id')
    list_filter = ('currency', 'interval')

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan', 'stripe_subscription_id', 'start_date', 'end_date', 'active', 'max_pcs')
    search_fields = ('user__email', 'stripe_subscription_id', 'plan__name')
    list_filter = ('active', 'plan', 'start_date')