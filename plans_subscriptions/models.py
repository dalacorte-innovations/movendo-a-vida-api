from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

User = get_user_model()

class Plan(models.Model):
    name = models.CharField(_("Nome do Plano"), max_length=50)
    stripe_price_id = models.CharField(_("ID do Preço no Stripe"), max_length=100, unique=True)
    description = models.TextField(_("Descrição"), blank=True, null=True)
    price = models.DecimalField(_("Preço"), max_digits=7, decimal_places=2)
    currency = models.CharField(_("Moeda"), max_length=10, default="usd")
    interval = models.CharField(_("Intervalo de cobrança"), max_length=20, help_text=_("Ex.: monthly, yearly"))

    def __str__(self):
        return self.name

class Subscription(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan, on_delete=models.SET_NULL, null=True)
    stripe_subscription_id = models.CharField(_("ID da Assinatura no Stripe"), max_length=100, unique=True)
    start_date = models.DateTimeField(_("Data de Início"))
    end_date = models.DateTimeField(_("Data de Término"), blank=True, null=True)
    active = models.BooleanField(_("Ativo"), default=True)
    max_pcs = models.IntegerField(verbose_name=_("Max PCs"), blank=True, null=True, default=0)

    def __str__(self):
        return f"{self.user.email} - {self.plan.name if self.plan else 'Sem Plano'}"