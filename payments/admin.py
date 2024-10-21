from django.contrib import admin
from .models import Product

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'stripe_product_id', 'price')
    search_fields = ('name', 'stripe_product_id')
    list_filter = ('price',)

    fieldsets = (
        (None, {'fields': ('name', 'stripe_product_id', 'price')}),
    )

admin.site.register(Product, ProductAdmin)
