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
    
    full_name = models.CharField(max_length=255, verbose_name=_("Full Name"), blank=True, null=True)
    phone = models.CharField(max_length=20, verbose_name=_("Phone Number"), blank=True, null=True)
    image = models.ImageField(upload_to="user_images/", verbose_name=_("Profile Picture"), blank=True, null=True)
    pix_key = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Chave PIX"))

    stripe_customer_id = models.CharField(max_length=255, null=True, blank=True)
    plan = models.CharField(max_length=255, null=True, blank=True)
    last_payment = models.DateField(null=True, blank=True)
    next_payment = models.DateField(null=True, blank=True)
    payment_made = models.BooleanField(default=False)
    
    referral_code = models.CharField(max_length=10, unique=True, blank=True, null=True)

    terms_accepted = models.BooleanField(default=False, verbose_name=_("Terms and Conditions Accepted"))
    terms_accepted_date = models.DateTimeField(null=True, blank=True, verbose_name=_("Terms Acceptance Date"))
    privacy_accepted = models.BooleanField(default=False, verbose_name=_("Privacy Policy Accepted"))
    privacy_accepted_date = models.DateTimeField(null=True, blank=True, verbose_name=_("Privacy Acceptance Date"))

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'full_name']

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")

    def __str__(self) -> str:
        return self.email

    def save(self, *args, **kwargs):
        if not self.full_name and self.first_name:
            self.full_name = self.first_name
        
        if not self.referral_code:
            self.referral_code = self.generate_referral_code()
        
        super().save(*args, **kwargs)

    def generate_referral_code(self):
        import random
        import string
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))


class UserReferral(models.Model):
    referred_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='referrals_made', verbose_name=_("Referred By"))
    referred_user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='referral', verbose_name=_("Referred User"))
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name=_("Referral Date"))

    class Meta:
        verbose_name = _("User Referral")
        verbose_name_plural = _("User Referrals")
        unique_together = ('referred_by', 'referred_user')

    def __str__(self):
        return f"{self.referred_user.email} referred by {self.referred_by.email}"


class WithdrawalRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_("User"))
    amount = models.DecimalField(_("Amount"), max_digits=10, decimal_places=2)
    request_date = models.DateTimeField(_("Request Date"), auto_now_add=True)
    status = models.CharField(
        _("Status"),
        max_length=20,
        choices=[("PENDING", _("Pending")), ("APPROVED", _("Approved")), ("REJECTED", _("Rejected"))],
        default="PENDING",
    )

    class Meta:
        verbose_name = _("Withdrawal Request")
        verbose_name_plural = _("Withdrawal Requests")

    def __str__(self):
        return f"Withdrawal request by {self.user.email} for R$ {self.amount:.2f}"