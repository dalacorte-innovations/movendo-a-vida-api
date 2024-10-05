
from django.conf import settings
from rest_framework.routers import DefaultRouter, SimpleRouter
from users.api.viewsets import UserViewSet

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

router.register("users", UserViewSet, basename="user")

app_name = "api"
urlpatterns = router.urls
