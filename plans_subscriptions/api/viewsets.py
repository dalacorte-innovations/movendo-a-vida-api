import stripe
import os
from dotenv import load_dotenv
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.conf import settings
from dotenv import load_dotenv
from django.utils import timezone
from datetime import timedelta

from plans_subscriptions.models import Plan, Subscription
from plans_subscriptions.api.serializers import PlanSerializer, SubscriptionSerializer

load_dotenv()
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
FRONTEND_SUCCESS_URL = os.getenv("FRONTEND_SUCCESS_URL")
FRONTEND_CANCEL_URL = os.getenv("FRONTEND_CANCEL_URL")

class PlanViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API para listar e recuperar os planos disponíveis.
    """
    queryset = Plan.objects.all()
    serializer_class = PlanSerializer
    permission_classes = [AllowAny]


class SubscriptionViewSet(viewsets.ModelViewSet):
    """
    API para gerenciar a assinatura do usuário.
    Somente o usuário autenticado poderá visualizar/alterar sua assinatura.
    """
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Subscription.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=["post"], url_path="create-checkout-session")
    def create_checkout_session(self, request):
        """
        Cria uma sessão de checkout do Stripe para o plano escolhido.
        O frontend deve enviar 'stripe_price_id' no body da requisição.
        """
        stripe_price_id = request.data.get("stripe_price_id")   

        if not stripe_price_id:
            return Response({"error": "O campo 'stripe_price_id' é obrigatório."}, status=400)

        try:
            plan = Plan.objects.get(stripe_price_id=stripe_price_id)
        except Plan.DoesNotExist:
            return Response({"error": "Plano não encontrado."}, status=404)

        try:
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                mode="subscription",
                line_items=[{
                    "price": plan.stripe_price_id,
                    "quantity": 1,
                }],
                customer_email=request.user.email,
                success_url=f"{FRONTEND_SUCCESS_URL}?session_id={{CHECKOUT_SESSION_ID}}",
                cancel_url=FRONTEND_CANCEL_URL,
                metadata={
                    "user_email": request.user.email,
                    "plan_id": str(plan.id),
                }
            )
            return Response({"checkout_url": session.url})

        except Exception as e:
            return Response({"error": str(e)}, status=500)

    @action(detail=False, methods=["get"], url_path="check-subscription")
    def check_subscription(self, request):
        """
        Retorna a assinatura do usuário autenticado.
        Caso não exista assinatura, retorna 404.
        """
        subscription = Subscription.objects.filter(user=request.user).first()
        if subscription:
            serializer = SubscriptionSerializer(subscription)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"error": "Assinatura não encontrada."}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=["post"], url_path="cancel-subscription")
    def cancel_subscription(self, request):
        """
        Cancela a assinatura do usuário. Neste exemplo, cancelamos a assinatura no Stripe 
        definindo que ela seja cancelada ao final do período (cancel_at_period_end=True)
        e atualizamos o status no banco de dados.
        """
        try:
            subscription = Subscription.objects.get(user=request.user)
        except Subscription.DoesNotExist:
            return Response({"error": "Assinatura não encontrada."}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            stripe.Subscription.modify(
                subscription.stripe_subscription_id,
                cancel_at_period_end=True
            )
        except Exception as e:
            return Response({"error": f"Erro ao cancelar a assinatura no Stripe: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        subscription.active = False
        subscription.end_date = subscription.end_date or (timezone.now() + timedelta(days=30))
        subscription.save()

        return Response({"message": "Assinatura cancelada. Ela permanecerá ativa até o final do período."}, status=status.HTTP_200_OK)