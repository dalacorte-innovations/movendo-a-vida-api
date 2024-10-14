# views.py
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from allauth.socialaccount.models import SocialAccount
from django.utils.translation import gettext_lazy as _
from rest_framework.permissions import AllowAny
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

from django.conf import settings

class CombinedLoginView(APIView):
    """
    View para processar login com `username` e `password` ou login com Google OAuth.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        if 'username' in request.data and 'password' in request.data:
            username = request.data.get('username')
            password = request.data.get('password')

            user = authenticate(request, username=username, password=password)
            if user is not None:
                token, created = Token.objects.get_or_create(user=user)

                return Response({
                    'token': token.key,
                    'name': f'{user.first_name} {user.last_name}',
                    'restricted_access': user.restricted_access,
                    'user_type': user.user_type
                }, status=status.HTTP_200_OK)
            else:
                return Response({"error": _("Invalid credentials")}, status=status.HTTP_401_UNAUTHORIZED)

        elif 'id_token' in request.data:
            id_token_google = request.data.get('id_token')

            try:
                id_info = id_token.verify_oauth2_token(id_token_google, google_requests.Request(), settings.SOCIALACCOUNT_PROVIDERS['google']['OAUTH2_CLIENT_ID'])

                if 'sub' in id_info:
                    try:
                        social_account = SocialAccount.objects.get(uid=id_info['sub'], provider='google')
                        user = social_account.user

                        token, created = Token.objects.get_or_create(user=user)

                        return Response({
                            'token': token.key,
                            'name': f'{user.first_name} {user.last_name}',
                            'restricted_access': user.restricted_access,
                            'user_type': user.user_type
                        }, status=status.HTTP_200_OK)

                    except SocialAccount.DoesNotExist:
                        return Response({'error': 'No social account found for this user'}, status=status.HTTP_404_NOT_FOUND)

            except ValueError as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"error": _("Invalid login request")}, status=status.HTTP_400_BAD_REQUEST)
