from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import status


class CustomObtainAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        user.check_and_update_restricted_access()

        token, created = Token.objects.get_or_create(user=user)

        name = f'{user.first_name} {user.last_name}'
        return Response({
            'token': token.key,
            'name': name,
            'restricted_access': user.restricted_access,
            'user_type': user.user_type
        }, status=status.HTTP_200_OK)
