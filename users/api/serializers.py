from django.contrib.auth import get_user_model
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from datetime import date
from users.models import UserReferral, UserType
from allauth.socialaccount.models import SocialAccount
import requests

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'full_name', 'phone', 
                  'user_type', 'stripe_customer_id', 'plan', 
                  'last_payment', 'next_payment', 'payment_made', 
                  'image']
        read_only_fields = ['id', 'username', 'user_type', 'stripe_customer_id']

    def update(self, instance, validated_data):
        image = validated_data.pop('image', None)
        if image:
            instance.image = image

        return super().update(instance, validated_data)
    

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, validators=[validate_password])
    id_token = serializers.CharField(write_only=True, required=False)
    facebook_token = serializers.CharField(write_only=True, required=False)
    referral_code = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ['email', 'first_name', 'password', 'phone', 'id_token', 'facebook_token', 'referral_code']

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
        referral_code = validated_data.pop('referral_code', None)
        
        if referral_code:
            try:
                referred_by = User.objects.get(referral_code=referral_code)
            except User.DoesNotExist:
                raise serializers.ValidationError({"referral_code": "Código de referência inválido."})

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
                    phone=validated_data.get('phone', ''),
                    user_type=UserType.USER_TYPE_COLLABORATOR,
                    payment_made=True,
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
                    phone=validated_data.get('phone', ''),
                    user_type=UserType.USER_TYPE_COLLABORATOR,
                    payment_made=True,
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
            phone=validated_data.get('phone'),
            user_type=UserType.USER_TYPE_COLLABORATOR,
            payment_made=True,
        )
        user.set_password(validated_data['password'])
        user.save()

        if referral_code:
            UserReferral.objects.create(
                referred_by=referred_by,
                referred_user=user
            )

        return user
    
    
class PasswordResetConfirmSerializer(serializers.Serializer):
    new_password1 = serializers.CharField(write_only=True)
    new_password2 = serializers.CharField(write_only=True)

    def validate(self, data):
        password = data.get("new_password1")
        password_confirm = data.get("new_password2")

        if password != password_confirm:
            raise serializers.ValidationError("As senhas não coincidem.")

        if len(password) < 8:
            raise serializers.ValidationError(
                "A senha deve ter pelo menos 8 caracteres."
            )

        if not any(char.isupper() for char in password):
            raise serializers.ValidationError(
                "A senha deve ter pelo menos um caractere MAIÚSCULO."
            )

        if not any(char.isdigit() for char in password):
            raise serializers.ValidationError("A senha deve ter pelo menos um número.")

        if not any(char in "!@#$%&*" for char in password):
            raise serializers.ValidationError(
                "A senha deve ter pelo menos um caractere especial (@, #, %, &, *)."
            )

        return data
    