from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

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
    user_type = models.CharField(max_length=1, choices=UserType.user_type_choices)
    email = models.EmailField(unique=True)
    
    stripe_customer_id = models.CharField(max_length=255, null=True, blank=True)
    plan = models.CharField(max_length=255, null=True, blank=True)
    last_payment = models.DateField(null=True, blank=True)
    next_payment = models.DateField(null=True, blank=True)
    payment_made = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")

    def __str__(self) -> str:
        return self.email
