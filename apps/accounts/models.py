"""Accounts database models."""

from django.db import models


class User(models.Model):
    """카카오 로그인 사용자 모델"""

    kakao_id = models.BigIntegerField(unique=True)
    nickname = models.CharField(max_length=255)
    profile_image = models.URLField(blank=True, null=True)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nickname

    @property
    def is_authenticated(self):
        return True


class RefreshToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="refresh_tokens")
    token = models.CharField(max_length=255, unique=True)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"RefreshToken(user={self.user_id})"
