from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.conf import settings
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from drf_spectacular.utils import extend_schema_field


class AccountSerializer(serializers.ModelSerializer):
    open_url = serializers.SerializerMethodField()
    avatar_url = serializers.SerializerMethodField()

    class Meta:
        model = get_user_model()
        fields = ['id', 'open_url', 'avatar_url', 'email', 'username', 'first_name', 'last_name']

    @extend_schema_field(serializers.CharField())
    def get_open_url(self, obj):
        request = self.context.get('request')
        return request.build_absolute_uri(reverse('image_board', kwargs={'object': obj.username}))

    @extend_schema_field(serializers.CharField())
    def get_avatar_url(self, obj):
        if not obj.avatar:
            return None

        request = self.context.get('request')
        return request.build_absolute_uri(settings.MEDIA_URL + str(obj.avatar))


class SignUpSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(required=True)
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=get_user_model().objects.all())]
    )
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password]
    )
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = get_user_model()
        fields = ('username', 'password', 'password2', 'email', 'first_name', 'last_name')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        user = get_user_model().objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data.get('last_name', str())
        )

        user.set_password(validated_data['password'])
        user.save()
        return user


class AccountSettingsSerializer(serializers.ModelSerializer):
    current_password = serializers.CharField(write_only=True, required=False)
    password1 = serializers.CharField(write_only=True, required=False)
    password2 = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = get_user_model()
        fields = ['first_name', 'last_name', 'email', 'username', 'avatar',
                  'current_password', 'password1', 'password2']

    def validate_email(self, value):
        user = self.instance
        if get_user_model().objects.filter(email__iexact=value).exclude(pk=user.pk).exists():
            raise serializers.ValidationError("A user with this email address already exists.")
        return value

    def validate_username(self, value):
        user = self.instance
        if get_user_model().objects.filter(username__iexact=value).exclude(pk=user.pk).exists():
            raise serializers.ValidationError("A user with this username already exists.")
        return value

    def validate(self, data):
        current_password = data.get('current_password')
        password1 = data.get('password1')
        password2 = data.get('password2')

        if password1 or password2:
            if not current_password:
                raise serializers.ValidationError("You must provide the current password to change your password.")
            if not self.instance.check_password(current_password):
                raise serializers.ValidationError("Current password is incorrect.")
            if password1 != password2:
                raise serializers.ValidationError("The two password fields didn’t match.")
        return data

    def update(self, instance, validated_data):
        if 'password1' in validated_data:
            instance.set_password(validated_data['password1'])
            validated_data.pop('password1', None)
            validated_data.pop('password2', None)
            validated_data.pop('current_password', None)

        avatar = validated_data.get('avatar')
        if avatar and instance.avatar:
            instance.avatar.delete(save=False)

        return super().update(instance, validated_data)
