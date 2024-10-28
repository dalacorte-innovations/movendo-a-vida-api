from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from core.models import Feedback, EmailMessage
from .serializers import EmailMessageSerializer, FeedbackSerializer

class FeedbackViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for viewing and editing feedback instances.
    """
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        if self.request.user.is_staff:
            return Feedback.objects.all()
        return Feedback.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class EmailMessageViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for viewing and editing EmailMessage instances.
    """
    queryset = EmailMessage.objects.all()
    serializer_class = EmailMessageSerializer
    permission_classes = (AllowAny,)

    def get_queryset(self):
        if self.request.user.is_staff:
            return EmailMessage.objects.all()
        return EmailMessage.objects.none()

    def perform_create(self, serializer):
        serializer.save()