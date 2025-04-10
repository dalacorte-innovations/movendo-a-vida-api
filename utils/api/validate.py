
from rest_framework import serializers


def validate_password(password1, password2):
    if password1 != password2:
        raise serializers.ValidationError("As senhas devem ser iguais.")
    if not any(c.isalpha() and c.isupper() for c in password1):
        raise serializers.ValidationError(
            "A senha precisa conter pelo menos uma letra maiúscula."
        )
    if len(password1) < 8:
        raise serializers.ValidationError("A senha deve ter pelo menos 8 caracteres.")
    if not any(c.isdigit() for c in password1):
        raise serializers.ValidationError(
            "A senha precisa conter pelo menos um número."
        )
    if password1.isalnum():
        raise serializers.ValidationError(
            "A senha precisa conter pelo menos um caractere especial."
        )
    return password1