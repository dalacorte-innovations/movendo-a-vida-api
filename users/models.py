from django.utils import timezone
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from payments.models import Product

class UserType:
    USER_TYPE_ROOT = "R"
    USER_TYPE_MANAGER = "M"
    USER_TYPE_COLLABORATOR = "C"

    user_type_choices = [
        (USER_TYPE_ROOT, _("Root")),
        (USER_TYPE_MANAGER, _("Manager")),
        (USER_TYPE_COLLABORATOR, _("Collaborator")),
    ]

class User(AbstractUser):
    user_type = models.CharField(verbose_name=_("User type"), max_length=1, choices=UserType.user_type_choices)
    email = models.EmailField(verbose_name=_("Email address"), unique=True)
    telephone = models.CharField(verbose_name=_("Telephone"), max_length=11, null=True, blank=True)
    registration_date = models.DateField(verbose_name=_("Registration date"), auto_now_add=True)
    last_payment = models.DateField(verbose_name=_("Last payment"), null=True, blank=True)
    
    stripe_customer_id = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("Stripe Customer ID"))
    subscription_id = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("Subscription ID"))
    plan = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("Current Plan"))
    payment_made = models.BooleanField(verbose_name=_("Payment made"), default=False)
    payment_status = models.CharField(max_length=20, choices=[('active', 'Active'), ('past_due', 'Past Due'), ('canceled', 'Canceled')], default='active')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")

    def __str__(self) -> str:
        return self.email
