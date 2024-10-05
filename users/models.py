from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.db.models import (
    CharField,
    EmailField,
    DateField,
    BooleanField,
)
from datetime import timedelta
from django.utils import timezone


class UserType:
    USER_TYPE_ROOT = "R"
    USER_TYPE_MANAGER = "M"
    USER_TYPE_COLLABORATOR = "C"

    user_type_choices = [
        (USER_TYPE_ROOT, _("Root")),
        (USER_TYPE_MANAGER, _("Manager")),
        (USER_TYPE_COLLABORATOR, _("Collaborator")),
    ]

    collaborator_type_choices = [
        (USER_TYPE_MANAGER, _("Manager")),
        (USER_TYPE_COLLABORATOR, _("Collaborator")),
    ]


class User(AbstractUser):
    user_type = CharField(verbose_name=_("User type"), max_length=1, choices=UserType.user_type_choices)
    email = EmailField(verbose_name=_("Email address"), unique=True)
    telephone = CharField(verbose_name=_("Telephone"), max_length=11, null=True, blank=True, unique=True)

    registration_date = DateField(verbose_name=_("Registration date"), auto_now_add=True)
    last_payment = DateField(verbose_name=_("Last payment"), null=True, blank=True)

    payment_made = BooleanField(verbose_name=_("Payment made"), default=True, null=True, blank=True)
    restricted_access = BooleanField(verbose_name=_("Restricted access"), default=False, null=True, blank=True)
    user_free = BooleanField(verbose_name=_("User free"), default=True, null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")

    def __str__(self) -> str:
        return self.email

    def check_and_update_restricted_access(self):
        if (self.user_free and (timezone.now().date() - self.registration_date > timedelta(days=7)) and
                self.payment_made):
            self.restricted_access = True
            self.save()
