from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings

class FeedbackCategory:
    PROBLEMA_TECNICO = "problema_tecnico"
    SUGESTAO_MELHORIA = "sugestao_melhoria"
    ELOGIO = "elogio"

    CATEGORY_CHOICES = [
        (PROBLEMA_TECNICO, _("Problema Técnico")),
        (SUGESTAO_MELHORIA, _("Sugestão de Melhoria")),
        (ELOGIO, _("Elogio")),
    ]
    
class Feedback(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="feedbacks",
        verbose_name=_("User")
    )

    stars = models.PositiveSmallIntegerField(
        verbose_name=_("Rating"),
        choices=[(i, f"{i} Star(s)") for i in range(1, 6)],
        default=0
    )

    comment = models.TextField(
        verbose_name=_("Comment"),
        max_length=500,
        blank=True,
        null=True,
    )

    category = models.CharField(
        max_length=20,
        choices=FeedbackCategory.CATEGORY_CHOICES,
        verbose_name=_("Category")
    )

    PUBLIC = "public"
    PRIVATE = "private"
    
    FEEDBACK_MODE_CHOICES = [
        (PUBLIC, _("Public")),
        (PRIVATE, _("Private")),
    ]

    feedback_mode = models.CharField(
        max_length=10,
        choices=FEEDBACK_MODE_CHOICES,
        verbose_name=_("Feedback Mode"),
        default=PRIVATE
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))

    class Meta:
        verbose_name = _("Feedback")
        verbose_name_plural = _("Feedbacks")
    
    def __str__(self):
        return f"Feedback by {self.user.email} - {self.get_category_display()} - {self.stars} Star(s)"


class EmailMessage(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name=_("Name")
    )

    email = models.EmailField(
        verbose_name=_("Email")
    )

    message = models.TextField(
        verbose_name=_("Message"),
        max_length=1000,
        help_text=_("Write your message here.")
    )

    viewed = models.BooleanField(
        default=False,
        verbose_name=_("Viewed")
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Created At")
    )

    class Meta:
        verbose_name = _("Email Message")
        verbose_name_plural = _("Email Messages")

    def __str__(self):
        return f"Message from {self.name} ({self.email})"
