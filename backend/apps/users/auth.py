from typing import Optional

from django.conf import settings
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import Users


class JWTAuthCookie(JWTAuthentication):
    def authenticate(self, request):
        raw_token = request.COOKIES.get(settings.SIMPLE_JWT["AUTH_COOKIE"]) or None
        if raw_token is None:
            return None

        validated_token = self.get_validated_token(raw_token)
        user = self.get_user(validated_token)
        return user, validated_token


class AuthForAdmin:
    def authenticate(
        self, request, username=None, password=None, **kwargs
    ) -> Optional[Users]:
        user = Users.objects.filter(username=username)
        user = user.first()
        if user is None:
            return None
        if not user.check_password(password):
            return None
        if not user.is_active:
            return None

        return user

    def get_user(self, user_id) -> Optional[Users]:
        try:
            user = Users.objects.get(pk=user_id)
            return user
        except Users.DoesNotExist:
            return None
