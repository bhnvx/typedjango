from rest_framework import status, permissions, mixins
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.tokens import RefreshToken

from backend import settings
from backend.apps.core.error import AlreadyExistsError
from .serializers import LoginSerializer
from .models import Users


class UserView(mixins.CreateModelMixin, GenericViewSet):
    serializer_class = LoginSerializer
    permission_classes = (permissions.AllowAny,)

    def perform_create(self, serializer: LoginSerializer):
        username = serializer.validated_data["username"]
        if Users.objects.filter(username=username).exists():
            raise AlreadyExistsError

        Users.objects.create_user(**serializer.validated_data)

    @action(detail=False, methods=["POST"])
    def login(self, request: Request) -> Response:
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data["username"]
        password = serializer.validated_data["password"]

        user = Users.objects.filter(username=username).first()
        if user is None:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        if not user.check_password(password):
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        if not user.is_active:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        return LoginResponse(user)


class LoginResponse(Response):
    def __init__(self, user: Users):
        super().__init__(status=status.HTTP_200_OK)

        token = RefreshToken.for_user(user)

        refresh = str(token)
        access = str(token.access_token)

        self.set_cookie(
            key=settings.SIMPLE_JWT["AUTH_COOKIE"],
            value=access,
            max_age=settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"].total_seconds(),
            secure=settings.SIMPLE_JWT["AUTH_COOKIE_SECURE"],
            httponly=settings.SIMPLE_JWT["AUTH_COOKIE_HTTP_ONLY"],
            samesite=settings.SIMPLE_JWT["AUTH_COOKIE_SAMESITE"],
        )

        self.data = {
            "refresh": refresh,
            "access": access,
        }
