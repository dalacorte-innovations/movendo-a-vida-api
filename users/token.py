from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from allauth.socialaccount.models import SocialAccount
from django.utils.translation import gettext_lazy as _
from rest_framework.permissions import AllowAny
import requests

class CombinedLoginView(APIView):
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
                    'user_type': user.user_type
                }, status=status.HTTP_200_OK)
            else:
                return Response({"error": _("Invalid credentials")}, status=status.HTTP_401_UNAUTHORIZED)

        elif 'access_token' in request.data:
            access_token = request.data.get('access_token')

            try:
                response = requests.get(
                    'https://www.googleapis.com/oauth2/v3/userinfo',
                    headers={'Authorization': f'Bearer {access_token}'}
                )
                user_info = response.json()

                if response.status_code != 200 or 'email' not in user_info:
                    return Response({'error': 'Failed to retrieve user information from Google.'}, status=status.HTTP_400_BAD_REQUEST)

                social_account = SocialAccount.objects.filter(uid=user_info['sub'], provider='google').first()

                if social_account:
                    user = social_account.user
                    token, created = Token.objects.get_or_create(user=user)

                    return Response({
                        'token': token.key,
                        'name': f'{user.first_name} {user.last_name}',
                        'user_type': user.user_type
                    }, status=status.HTTP_200_OK)
                else:
                    return Response({'error': 'No social account found for this user'}, status=status.HTTP_404_NOT_FOUND)

            except requests.RequestException as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        elif 'facebook_token' in request.data:
            facebook_token = request.data.get('facebook_token')

            try:
                response = requests.get(
                    f'https://graph.facebook.com/me?fields=id,name,email&access_token={facebook_token}'
                )
                user_info = response.json()

                if response.status_code != 200 or 'email' not in user_info:
                    return Response({'error': 'Failed to retrieve user information from Facebook.'}, status=status.HTTP_400_BAD_REQUEST)

                social_account = SocialAccount.objects.filter(uid=user_info['id'], provider='facebook').first()

                if social_account:
                    user = social_account.user
                    token, created = Token.objects.get_or_create(user=user)

                    return Response({
                        'token': token.key,
                        'name': f'{user.first_name} {user.last_name}',
                        'user_type': user.user_type
                    }, status=status.HTTP_200_OK)
                else:
                    return Response({'error': 'No social account found for this user'}, status=status.HTTP_404_NOT_FOUND)

            except requests.RequestException as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"error": _("Invalid login request")}, status=status.HTTP_400_BAD_REQUEST)
