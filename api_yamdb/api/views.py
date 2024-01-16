from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken
from reviews.models import User

from api_yamdb.settings import DEFAULT_FROM_EMAIL

from .permissions import IsSuperUserOrIsAdminOnly
from .serializers import SignupSerializer, TokenSerializer, UserSerializer


@api_view(['POST'])
def signup(request):
    serializer = SignupSerializer(data=request.data)
    if serializer.is_valid():
        username = serializer.validated_data.get('username')
        email = serializer.validated_data.get('email')
        user, created = User.objects.get_or_create(
            username=username, email=email
        )
        if created:
            confirmation_code = default_token_generator.make_token(user)
            send_mail(
                subject='Регистрация в YaMDb',
                message=f'Ваш проверочный код: {confirmation_code}',
                from_email=DEFAULT_FROM_EMAIL,
                recipient_list=[user.email]
            )
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(
                {"error": "Пользователь уже существует"},
                status=status.HTTP_400_BAD_REQUEST
            )
    else:
        return Response(
            {"error": "Отсутствует обязательное поле или оно некорректно"},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['POST'])
def get_token(request):
    serializer = TokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = get_object_or_404(
        User, username=serializer.validated_data.get('username')
    )
    if default_token_generator.check_token(
        user, serializer.validated_data.get('confirmation_code')
    ):
        token = AccessToken.for_user(user)
        return Response({'token': token}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsSuperUserOrIsAdminOnly,)
    search_fields = ('username',)
    pagination_class = PageNumberPagination

    @action(
        detail=False,
        methods=['get', 'patch', 'delete'],
        url_path=r'(?P<username>[\w.@+-]+)',
    )
    def get_user_by_username(self, request, username):
        """Получает данные пользователя по его username"""
        user = get_object_or_404(User, username=username)
        if request.method == 'PATCH':
            serializer = UserSerializer(user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        elif request.method == 'DELETE':
            user.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=['get', 'patch'],
        url_path='me',
    )
    def get_users_own_profile(self, request):
        """Пользователь получает информацию о себе и может редактировать её."""
        if request.method == 'PATCH':
            serializer = UserSerializer(
                request.user, data=request.data,
                partial=True, context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            serializer.save(role=request.user.role)
            return Response(serializer.data, status=status.HTTP_200_OK)
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
