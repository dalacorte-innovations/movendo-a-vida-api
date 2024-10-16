from users.models import User
from .serializers import PasswordResetConfirmSerializer, UserSerializer, RegisterSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import generics, viewsets
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from users.forms import (
    PasswordResetForm,
)
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


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)


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
                        "domain": config("DOMAIN"),
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



