from django.core.validators import MaxValueValidator, MinValueValidator
from rest_framework import serializers
from rest_framework.generics import get_object_or_404

from reviews.models import Category, Comment, Genre, Review, Title, User
from api_yamdb.settings import MAX_EMAIL_LENGTH, MAX_LENGTH


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role'
        )
        model = User

    def validate_username(self, username):
        if username in 'me':
            raise serializers.ValidationError(
                'Использовать имя "me" запрещено'
            )
        return username


class UserEditSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        read_only_fields = ('role',)


class TokenSerializer(serializers.Serializer):
    username = serializers.RegexField(
        regex=r'^[\w.@+-]+$',
        max_length=MAX_LENGTH,
        required=True
    )
    confirmation_code = serializers.CharField(
        max_length=MAX_LENGTH,
        required=True
    )


class SignupSerializer(serializers.Serializer):

    email = serializers.EmailField(
        max_length=MAX_EMAIL_LENGTH, required=True
    )
    username = serializers.RegexField(
        regex=r'^[\w.@+-]+$',
        max_length=MAX_LENGTH,
        required=True
    )

    class Meta:
        model = User
        fields = ('email', 'username')

    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError(
                'Использовать имя "me" запрещено'
            )
        return value


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ('name', 'slug')


class TitleSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(
        read_only=True, many=True
    )
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        model = Title
        fields = ('id', 'name', 'year',
                  'description', 'genre', 'category', 'rating')


class TitleCreateSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(), slug_field='slug'
    )
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(), slug_field='slug', many=True
    )

    class Meta:
        model = Title
        fields = '__all__'

    def to_representation(self, instance):
        return {
            'id': instance.id,
            'name': instance.name,
            'year': instance.year,
            'rating': None,
            'description': instance.description,
            'genre': GenreSerializer(instance.genre.all(), many=True).data,
            'category': CategorySerializer(instance.category).data,
        }


class ReviewSerializer(serializers.ModelSerializer):

    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )
    score = serializers.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(10)]
    )

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')

    def validate(self, data):
        """Запрещает пользователям оставлять повторные отзывы."""
        request = self.context["request"]
        if request.method == "POST":
            author = request.user
            title_id = self.context["view"].kwargs.get("title_id")
            title = get_object_or_404(Title, pk=title_id)
            if Review.objects.filter(author=author, title=title).exists():
                raise serializers.ValidationError(
                    'Вы уже оставляли отзыв на это произведение.'
                )
        return data


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')
