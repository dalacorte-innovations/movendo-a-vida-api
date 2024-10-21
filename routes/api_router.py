from django.conf import settings
from rest_framework.routers import DefaultRouter, SimpleRouter
from users.api.viewsets import UserViewSet
from django.urls import path
from payments.views import stripe_webhook
if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

router.register("users", UserViewSet, basename="user")

urlpatterns = router.urls + [
    path('stripe/webhook/', stripe_webhook, name='stripe-webhook'),

]
