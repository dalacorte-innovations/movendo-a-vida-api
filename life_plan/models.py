from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class LifePlan(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="life_plans",
        verbose_name="User"
    )
    name = models.CharField(max_length=100, verbose_name="Name of Life Plan")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")

    def __str__(self):
        return f"Life Plan for {self.user.email}"
    
class LifePlanItem(models.Model):
    CATEGORY_CHOICES = [
        ('receitas', _("Receitas")),
        ('estudos', _("Estudos")),
        ('custos', _("Custos")),
        ('lucro_prejuizo', _("Lucro/Prejuízo")),
        ('investimentos', _("Investimentos")),
        ('realizacoes', _("Realizações")),
        ('intercambio', _("Intercâmbio")),
        ('empresas', _("Empresas")),
    ]

    life_plan = models.ForeignKey(
        LifePlan,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Life Plan"
    )
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, verbose_name="Category")
    name = models.CharField(max_length=100, verbose_name="Item Name")
    value = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Value")
    date = models.DateField(verbose_name="Date")
    meta = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Meta")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")

    def __str__(self):
        return f"{self.category} - {self.name}: {self.value}"
