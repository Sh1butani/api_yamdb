from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.filters import SearchFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import (IsAuthenticated, AllowAny)
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken
from reviews.models import Category, Genre, Title, User, Review, Comment

from api_yamdb.settings import DEFAULT_FROM_EMAIL
from .filters import TitleFilter
from .permissions import (
    IsSuperUserOrIsAdminOnly,
    IsAdminOrReadOnly,
    IsAdminModeratorAuthorOrReadOnly
)
from .serializers import (
    CategorySerializer,
    GenreSerializer,
    ReviewSerializer,
    SignupSerializer,
    TitleCreateSerializer,
    TitleSerializer,
    CommentSerializer,
    TokenSerializer,
    UserSerializer,
    UserEditSerializer,
)


@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    """
    Добавляет нового пользователя. Отправляет код подтверждения на почту.
    """
    serializer = SignupSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    try:
        username = serializer.validated_data.get('username')
        email = serializer.validated_data.get('email')
        user, created = User.objects.get_or_create(
            username=username, email=email
        )
    except IntegrityError:
        return Response(
            'Эта электронная почта уже занята!' if User.objects.filter(
                email=serializer.validated_data.get('email')
            ).exists()
            else 'Это имя пользователя уже занято!',
            status.HTTP_400_BAD_REQUEST)
    confirmation_code = default_token_generator.make_token(user)
    send_mail(
        subject='Регистрация в YaMDb',
        message=f'Ваш проверочный код: {confirmation_code}',
        from_email=DEFAULT_FROM_EMAIL,
        recipient_list=[user.email]
    )
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def get_token(request):
    """Возвращает пользователю токен для авторизации."""
    serializer = TokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = get_object_or_404(
        User, username=serializer.validated_data.get('username')
    )
    if default_token_generator.check_token(
        user, serializer.validated_data.get('confirmation_code')
    ):
        return Response(
            {'token': str(AccessToken.for_user(user))},
            status=status.HTTP_200_OK)
    return Response(
        {'confirmation_code': 'Некорректный код подтверждения'},
        status=status.HTTP_400_BAD_REQUEST
    )


class UserViewSet(viewsets.ModelViewSet):
    """Вьюсет пользователя."""
    queryset = User.objects.order_by('username').all()
    serializer_class = UserSerializer
    permission_classes = (IsSuperUserOrIsAdminOnly,)
    pagination_class = PageNumberPagination
    filter_backends = [SearchFilter]
    lookup_field = 'username'
    search_fields = ['username']
    http_method_names = ['get', 'list', 'post', 'patch', 'delete']

    @action(
        detail=False,
        methods=['get', 'patch'],
        url_path='me',
        permission_classes=(IsAuthenticated,),
        serializer_class=UserEditSerializer,
    )
    def get_users_own_profile(self, request):
        """Получает информацию о пользователе и может редактировать её."""
        user = request.user
        if request.method == "PATCH":
            serializer = self.get_serializer(
                user, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
        elif request.method == 'DELETE':
            user.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            serializer = self.get_serializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CreateListDeleteViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
):

    filter_backends = (SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class CategoryViewSet(CreateListDeleteViewSet):
    """Вьюсет категорий."""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrReadOnly,)


class GenreViewSet(CreateListDeleteViewSet):
    """Вьюсет жанров."""
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAdminOrReadOnly,)


class TitleViewSet(viewsets.ModelViewSet):
    """Вьюсет произведений."""
    queryset = Title.objects.all().annotate(rating=Avg('reviews__score'))
    serializer_class = TitleSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter
    pagination_class = PageNumberPagination
    http_method_names = ['get', 'list', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return TitleSerializer
        return TitleCreateSerializer


class CommentViewSet(viewsets.ModelViewSet):
    """Вьюсет комментариев."""
    serializer_class = CommentSerializer
    permission_classes = (IsAdminModeratorAuthorOrReadOnly,)
    pagination_class = PageNumberPagination
    http_method_names = ['get', 'list', 'post', 'patch', 'delete']

    def get_queryset(self):
        review_id = get_object_or_404(Review, pk=self.kwargs.get('review_id'))
        return Comment.objects.filter(review=review_id)

    def perform_create(self, serializer):
        review = get_object_or_404(Review, pk=self.kwargs.get('review_id'))
        serializer.save(
            review=review,
            author=self.request.user
        )


class ReviewViewSet(viewsets.ModelViewSet):
    """Вьюсет отзывов."""
    serializer_class = ReviewSerializer
    permission_classes = (IsAdminModeratorAuthorOrReadOnly,)
    pagination_class = PageNumberPagination
    http_method_names = ['get', 'list', 'post', 'patch', 'delete']

    def get_queryset(self):
        return get_object_or_404(
            Title, pk=self.kwargs.get('title_id')
        ).reviews.all()

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            title=get_object_or_404(Title, id=self.kwargs.get('title_id'))
        )
