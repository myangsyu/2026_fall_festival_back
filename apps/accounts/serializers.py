"""Accounts request and response serializers."""

from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "kakao_id", "nickname", "profile_image", "createdAt", "updatedAt"]


class LoginSerializer(serializers.Serializer):
    code = serializers.CharField(required=True)  # 카카오 인증 코드


class RefreshTokenSerializer(serializers.Serializer):
    refresh_token = serializers.CharField(required=True)
