from django.conf import settings
from rest_framework.routers import DefaultRouter, SimpleRouter
from core.api.viewsets import EmailMessageViewSet, FeedbackViewSet
from users.api.viewsets import UserViewSet
from django.urls import path
from payments.views import stripe_webhook
if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

router.register("users", UserViewSet, basename="user")
router.register("feedback", FeedbackViewSet, basename="feedback")
router.register("email-message", EmailMessageViewSet, basename="email-message")

urlpatterns = router.urls + [
    path('stripe/webhook/', stripe_webhook, name='stripe-webhook'),

]
