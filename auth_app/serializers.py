from rest_framework.serializers import ModelSerializer
from .models import User, Message


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['name', 'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data: dict) -> User:
        """Create User instance with hashed password"""
        password = validated_data.pop('password', '')
        user = self.Meta.model(**validated_data)
        if password:
            user.set_password(raw_password=password)
            user.save()
            return user


class MessageSerializer(ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'user', 'text']
