from users.models import User, UserReferral, WithdrawalRequest
from plans_subscriptions.models import Subscription
from .serializers import PasswordResetConfirmSerializer, UserSerializer, RegisterSerializer, WithdrawalRequestSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import generics, viewsets
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from users.forms import (
    PasswordResetForm,
)
from django.db.models import Sum
from django.db.models import Count
from django.core.mail import send_mail, BadHeaderError
from django.contrib.auth import get_user_model
from django.db.models import Q
from decouple import config
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.contrib.auth.tokens import default_token_generator
from django.http import HttpResponse
from django.utils.http import urlsafe_base64_decode
from rest_framework.decorators import action
from utils.api.validate import validate_password
from rest_framework import serializers


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    def partial_update(self, request, *args, **kwargs):
        user = request.user
        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get', 'patch'], permission_classes=[IsAuthenticated])
    def me(self, request):
        user = request.user
        if request.method == 'PATCH':
            serializer = UserSerializer(user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        else:
            serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def accept_terms_and_privacy(self, request):
        user = request.user
        accept_terms = request.data.get('accept_terms', False)
        accept_privacy = request.data.get('accept_privacy', False)

        from django.utils import timezone
        current_time = timezone.now()

        if accept_terms:
            user.terms_accepted = True
            user.terms_accepted_date = current_time

        if accept_privacy:
            user.privacy_accepted = True
            user.privacy_accepted_date = current_time

        if accept_terms or accept_privacy:
            user.save()

        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=["patch"], permission_classes=[IsAuthenticated])
    def change_password(self, request):
        user = request.user
        current_password = request.data.get("current_password")
        new_password1 = request.data.get("password1")
        new_password2 = request.data.get("password2")

        if not current_password or not new_password1 or not new_password2:
            return Response(
                {"detail": "Todos os campos de senha são obrigatórios."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not user.check_password(current_password):
            return Response(
                {"detail": "Senha atual incorreta."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if new_password1 != new_password2:
            return Response(
                {"detail": "As novas senhas não coincidem."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            validate_password(new_password1, new_password2)
        except serializers.ValidationError as e:
            return Response({"detail": e.detail[0]}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password1)
        user.save()
        return Response(
            {"detail": "Senha alterada com sucesso."}, status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def user_stats(self, request):
        total_referrals = UserReferral.objects.values('referred_by').annotate(referral_count=Count('referred_user')).aggregate(total_referrals=Count('referred_by'))['total_referrals'] or 0

        active_subscriptions = Subscription.objects.filter(active=True).select_related('plan')

        available_amount = 0
        for subscription in active_subscriptions:
            plan_name = subscription.plan.name if subscription.plan else ""
            if plan_name == "Basic":
                available_amount += 10
            elif plan_name == "Premium":
                available_amount += 20
            elif plan_name == "Profissional":
                available_amount += 270

        completed_withdrawals = WithdrawalRequest.objects.filter(user=request.user, status="APPROVED")
        total_completed = completed_withdrawals.aggregate(total=Sum('amount'))['total'] or 0

        pending_withdrawals = WithdrawalRequest.objects.filter(user=request.user, status="PENDING")
        total_pending = pending_withdrawals.aggregate(total=Sum('amount'))['total'] or 0

        remaining_amount = available_amount - total_completed - total_pending
        remaining_amount = max(remaining_amount, 0)
        formatted_available_amount = f"R$ {remaining_amount:.2f}"

        data = {
            "total_referrals": total_referrals,
            "completed_contracts": active_subscriptions.count(),
            "available_amount": formatted_available_amount,
        }

        return Response(data, status=200)
        
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def request_withdrawal(self, request):
        user = request.user
        if not user.pix_key:
            return Response(
                {"detail": "Você precisa preencher sua chave PIX para solicitar um saque."},
                status=status.HTTP_400_BAD_REQUEST
            )

        data = {"amount": request.data.get("amount")}

        serializer = WithdrawalRequestSerializer(data=data, context={'request': request})

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def list_withdrawals(self, request):
        withdrawals = WithdrawalRequest.objects.filter(user=request.user)
        serializer = WithdrawalRequestSerializer(withdrawals, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class WithdrawalRequestCreateAPIView(viewsets.ModelViewSet):
    queryset = WithdrawalRequest.objects.all()
    serializer_class = WithdrawalRequestSerializer
    permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        """ Override create method to handle validation """
        response = super().create(request, *args, **kwargs)
        return response
    
class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer


class PasswordResetRequest(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        password_reset_form = PasswordResetForm(request.data)
        if password_reset_form.is_valid():
            email = password_reset_form.cleaned_data["email"]
            associated_users = get_user_model().objects.filter(Q(email=email))
            if associated_users.exists():
                for user in associated_users:
                    subject = "Redefinição de senha solicitada"
                    email_template_name = "password_reset_email_api"
                    c = {
                        "email": user.email,
                        "domain": config("DOMAIN_APP"),
                        "site_name": "Portal CG Contadores",
                        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                        "token": default_token_generator.make_token(user),
                    }
                    email_content = render_to_string(email_template_name, c)
                    try:
                        send_mail(
                            subject,
                            email_content,
                            "contato@cgcontadores.com.br",
                            [user.email],
                            fail_silently=False,
                        )
                    except BadHeaderError:
                        return HttpResponse("Invalid header found.")
                    return Response(
                        {
                            "message": "As instruções de redefinição de senha foram enviadas para seu e-mail."
                        },
                        status=status.HTTP_200_OK,
                    )
            return Response(
                {"error": "Nenhum usuário está associado a este e-mail."},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(password_reset_form.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomPasswordResetConfirmViewAPI(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, uidb64, token, *args, **kwargs):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            try:
                uid = urlsafe_base64_decode(uidb64).decode()
                user = User.objects.get(pk=uid)
            except (TypeError, ValueError, OverflowError, User.DoesNotExist):
                user = None

            if user is not None and default_token_generator.check_token(user, token):
                user.set_password(serializer.validated_data["new_password1"])
                user.save()
                return Response(
                    {"detail": "Senha redefinida com sucesso."},
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {"detail": "Token inválido ou expirado."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



