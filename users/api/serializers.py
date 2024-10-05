from django.contrib.auth import get_user_model
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from datetime import date
from users.models import UserType

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name',
                  'telephone', 'last_name', 'user_type', 'seven_days',
                  'registration_date', 'payment_open']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ['email', 'first_name', 'password', 'telephone']

    def validate_email(self, value):
        lower_email = value.lower()
        if User.objects.filter(email=lower_email).exists():
            raise serializers.ValidationError("Este e-mail já está sendo usado.")
        return lower_email

    def create(self, validated_data):
        validated_data['email'] = validated_data['email'].lower()
        
        print(validated_data)
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
