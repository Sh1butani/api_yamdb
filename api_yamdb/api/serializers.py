from rest_framework import serializers

from reviews.models import Title, Genre, Category, User, MAX_LENGTH


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role'
        )
        model = User

    def validate_username(self, username):
        if username in 'me':
            raise serializers.ValidationError(
                'Использовать имя me запрещено'
            )
        return username


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

    class Meta:
        model = User
        fields = ('email', 'username')

        def validate(self, data):
            """Запрещает пользователям присваивать себе имя 'me'
            и использовать такие же username и email, как при регистрации."""
            if data.get('username') == 'me':
                raise serializers.ValidationError(
                    'Использовать имя me запрещено'
                )
            elif User.objects.filter(username=data.get('username')):
                raise serializers.ValidationError(
                    'Пользователь с таким username уже существует'
                )
            elif User.objects.filter(email=data.get('email')):
                raise serializers.ValidationError(
                    'Пользователь с таким email уже существует'
                )
            return data


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
        fields = (
            'id', 'name', 'year', 'rating', 'description', 'genre', 'category'
        )


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
