from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from core.models import Feedback, EmailMessage
from .serializers import EmailMessageSerializer, FeedbackSerializer

class FeedbackViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for viewing and editing feedback instances.
    """
    serializer_class = FeedbackSerializer
    permission_classes = (AllowAny,)

    def get_queryset(self):
        """
        Retorna os feedbacks de acordo com o usuário autenticado.
        Se o usuário for staff, retorna os feedbacks com active_landing_page=True, limitados aos 5 mais recentes.
        Se não for staff, retorna somente os feedbacks do próprio usuário.
        """
        return Feedback.objects.filter(active_landing_page=True).order_by('-created_at')[:5]

    def perform_create(self, serializer):
        """
        Salva o feedback associado ao usuário autenticado.
        """
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