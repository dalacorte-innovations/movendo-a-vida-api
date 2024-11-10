from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from life_plan.models import LifePlan, LifePlanItem
from .serializers import LifePlanSerializer, LifePlanItemSerializer

class LifePlanViewSet(viewsets.ModelViewSet):
    queryset = LifePlan.objects.all()
    serializer_class = LifePlanSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return LifePlan.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class LifePlanItemViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for viewing and editing LifePlanItem instances.
    """
    queryset = LifePlanItem.objects.all()
    serializer_class = LifePlanItemSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        if self.request.user.is_staff:
            return LifePlanItem.objects.all()
        return LifePlanItem.objects.filter(life_plan__user=self.request.user)

    def perform_create(self, serializer):
        serializer.save()
