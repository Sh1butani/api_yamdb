from rest_framework import serializers

from reviews.models import User, MAX_LENGTH


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
