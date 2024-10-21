from django.db import models
from django.utils.translation import gettext_lazy as _

class Product(models.Model):
    name = models.CharField(max_length=255, verbose_name=_("Plan Name"))
    stripe_product_id = models.CharField(max_length=255, unique=True, verbose_name=_("Stripe Product ID"))
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Price"))

    def __str__(self):
        return self.name
