from django.contrib.auth import get_user_model
from django.contrib.auth.forms import SetPasswordForm
from django_restql.mixins import DynamicFieldsMixin
from rest_framework import serializers
from rest_framework.authtoken.models import Token

User = get_user_model()


class UserSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    new_password1 = serializers.CharField(max_length=128, write_only=True)
    new_password2 = serializers.CharField(max_length=128, write_only=True)
    token = serializers.SerializerMethodField('get_token')

    class Meta:
        model = User
        fields = [
            'token',
            'id',
            'username',
            'email',
            'new_password1',
            'new_password2',
            'last_order_date',
            'first_order_date',
            'average_order_value',
            'wish_list_count',
        ]

    def validate(self, attrs):
        password = attrs.get('new_password1', None)
        if password is None:
            return attrs

        set_password_form = SetPasswordForm(
            user=self, data=attrs
        )
        if not set_password_form.is_valid():
            raise serializers.ValidationError(set_password_form.errors)
        return attrs

    def create(self, validated_data):
        try:
            validated_data.pop('new_password1')
            new_password2 = validated_data.pop('new_password2')
            user = super(UserSerializer, self).create(validated_data)
        except Exception as e:
            raise serializers.ValidationError({"error": [e]})
        user.set_password(new_password2)
        user.save()
        return user

    def update(self, instance, validated_data):
        validated_data.pop('new_password1', None)
        validated_data.pop('new_password2', None)

        return super(UserSerializer, self).update(instance, validated_data)

    def get_token(self, user):
        return None


class UserLoginDataSerializer(UserSerializer):

    def get_token(self, user):
        token, created = Token.objects.get_or_create(user=user)
        return token.key


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)
