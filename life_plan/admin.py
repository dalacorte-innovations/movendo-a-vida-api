from django.contrib import admin
from .models import LifePlan, LifePlanItem

class LifePlanItemInline(admin.TabularInline):
    model = LifePlanItem
    extra = 1
    fields = ('category', 'name', 'value', 'date', 'created_at')
    readonly_fields = ('created_at',)

class LifePlanAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'name', 'created_at', 'updated_at', 
        'get_total_receitas', 'get_total_estudos', 'get_total_custos', 'get_total_lucro_prejuizo'
    )
    search_fields = ('user__email', 'user__username', 'name')
    list_filter = ('created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [LifePlanItemInline]

    fieldsets = (
        (None, {'fields': ('user', 'name')}),
        ('Dates', {'fields': ('created_at', 'updated_at')}),
    )

    def get_total_receitas(self, obj):
        return self.get_category_total(obj, 'receitas')
    get_total_receitas.short_description = 'Total Receitas'

    def get_total_estudos(self, obj):
        return self.get_category_total(obj, 'estudos')
    get_total_estudos.short_description = 'Total Estudos'

    def get_total_custos(self, obj):
        return self.get_category_total(obj, 'custos')
    get_total_custos.short_description = 'Total Custos'

    def get_total_lucro_prejuizo(self, obj):
        return self.get_category_total(obj, 'lucro_prejuizo')
    get_total_lucro_prejuizo.short_description = 'Total Lucro/Prejuízo'

    def get_category_total(self, obj, category):
        return sum(item.value for item in obj.items.filter(category=category))

class LifePlanItemAdmin(admin.ModelAdmin):
    list_display = (
        'life_plan', 'category', 'name', 'value', 'date', 'created_at'
    )
    search_fields = ('life_plan__user__email', 'life_plan__user__username', 'name')
    list_filter = ('category', 'date', 'created_at')

admin.site.register(LifePlan, LifePlanAdmin)
admin.site.register(LifePlanItem, LifePlanItemAdmin)
