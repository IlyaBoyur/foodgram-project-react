from django.contrib.auth import get_user_model
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions as django_exceptions

User = get_user_model()


class UserReadSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.BooleanField(read_only=True)

    class Meta:
        model = User
        fields = ('email', 'username', 'first_name', 'last_name', 'id',
                  'is_subscribed')


class UserWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'password')

    def validate(self, attrs):
        user = User(**attrs)
        password = attrs.get("password")
        try:
            validate_password(password, user)
        except django_exceptions.ValidationError as error:
            raise serializers.ValidationError(
                {"password": serializers
                             .as_serializer_error(error)["non_field_errors"]}
            )
        return attrs

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)