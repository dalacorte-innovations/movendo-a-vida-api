from django.conf import settings
from rest_framework.routers import DefaultRouter, SimpleRouter
from core.api.viewsets import EmailMessageViewSet, FeedbackViewSet
from life_plan.api.viewsets import LifePlanViewSet, LifePlanItemViewSet
from users.api.viewsets import UserViewSet
from django.urls import path
from plans_subscriptions.payments import stripe_webhook

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

API_PREFIX = "api/v1/"

router.register("users", UserViewSet, basename="user")
router.register("feedback", FeedbackViewSet, basename="feedback")
router.register("email-message", EmailMessageViewSet, basename="email-message")
router.register("life-plan", LifePlanViewSet, basename="life-plan")
router.register("life-plan-item", LifePlanItemViewSet, basename="life-plan-item")


urlpatterns = router.urls + [
    path(f'{API_PREFIX}payments/webhook/stripe/', stripe_webhook, name='stripe-webhook'),
]
