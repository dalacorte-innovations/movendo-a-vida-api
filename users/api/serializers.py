from django.contrib.auth import get_user_model
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from datetime import date
from users.models import UserType
from allauth.socialaccount.models import SocialAccount
import requests

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name',
                  'telephone', 'last_name', 'user_type', 'seven_days',
                  'registration_date', 'payment_open']

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, validators=[validate_password])
    id_token = serializers.CharField(write_only=True, required=False)
    facebook_token = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ['email', 'first_name', 'password', 'telephone', 'id_token', 'facebook_token']

    def validate(self, attrs):
        id_token_google = attrs.get('id_token')
        facebook_token = attrs.get('facebook_token')

        if not id_token_google and not facebook_token:
            if not attrs.get('password'):
                raise serializers.ValidationError({"password": "Password is required for non-social registration."})

        return attrs

    def validate_email(self, value):
        lower_email = value.lower()
        if User.objects.filter(email=lower_email).exists():
            raise serializers.ValidationError("Este e-mail já está sendo usado.")
        return lower_email

    def create(self, validated_data):
        id_token_google = validated_data.pop('id_token', None)
        facebook_token = validated_data.pop('facebook_token', None)
        
        if id_token_google:
            try:
                response = requests.get(
                    'https://www.googleapis.com/oauth2/v3/userinfo',
                    headers={'Authorization': f'Bearer {id_token_google}'}
                )
                user_info = response.json()
                
                if response.status_code != 200 or 'email' not in user_info:
                    raise serializers.ValidationError({"id_token": "Invalid Google access token"})

                social_account = SocialAccount.objects.filter(uid=user_info['sub'], provider='google').first()

                if social_account:
                    raise serializers.ValidationError("Este usuário já está registrado com uma conta Google.")

                user = User.objects.create(
                    email=user_info['email'],
                    username=user_info['email'],
                    first_name=user_info.get('given_name', ''),
                    last_name=user_info.get('family_name', ''),
                    telephone=validated_data.get('telephone', ''),
                    user_type=UserType.USER_TYPE_COLLABORATOR,
                    registration_date=date.today(),
                    payment_made=True,
                    restricted_access=False,
                    user_free=True,
                )
                user.set_unusable_password()
                user.save()

                SocialAccount.objects.create(user=user, uid=user_info['sub'], provider='google')
                return user

            except requests.RequestException as e:
                raise serializers.ValidationError({"id_token": "Failed to fetch user info from Google."})

        if facebook_token:
            try:
                response = requests.get(
                    'https://graph.facebook.com/me',
                    params={'fields': 'id,email,first_name,last_name', 'access_token': facebook_token}
                )
                user_info = response.json()

                if response.status_code != 200 or 'email' not in user_info:
                    raise serializers.ValidationError({"facebook_token": "Invalid Facebook access token"})

                social_account = SocialAccount.objects.filter(uid=user_info['id'], provider='facebook').first()

                if social_account:
                    raise serializers.ValidationError("Este usuário já está registrado com uma conta Facebook.")

                user = User.objects.create(
                    email=user_info['email'],
                    username=user_info['email'],
                    first_name=user_info.get('first_name', ''),
                    last_name=user_info.get('last_name', ''),
                    telephone=validated_data.get('telephone', ''),
                    user_type=UserType.USER_TYPE_COLLABORATOR,
                    registration_date=date.today(),
                    payment_made=True,
                    restricted_access=False,
                    user_free=True,
                )
                user.set_unusable_password()
                user.save()

                SocialAccount.objects.create(user=user, uid=user_info['id'], provider='facebook')
                return user

            except requests.RequestException as e:
                raise serializers.ValidationError({"facebook_token": "Failed to fetch user info from Facebook."})

        validated_data['email'] = validated_data['email'].lower()
        user = User.objects.create(
            email=validated_data['email'],
            username=validated_data['email'],
            first_name=validated_data['first_name'],
            telephone=validated_data.get('telephone'),
            user_type=UserType.USER_TYPE_COLLABORATOR,
            registration_date=date.today(),
            payment_made=True,
            restricted_access=False,
            user_free=True,
        )
        user.set_password(validated_data['password'])
        user.save()
        return user
