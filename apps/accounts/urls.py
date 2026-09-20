"""Accounts API routes."""

from django.urls import path

from .views import KakaoLoginView, TokenRefreshView

urlpatterns = [
    path("login/", KakaoLoginView.as_view(), name="kakao-login"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
]
