# Python
# Django
# Rest Framework
from django.contrib.auth.models import User
from rest_framework.serializers import ModelSerializer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
# Local

class LoginSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token['username'] = user.username
        token['firstname'] = user.first_name
        token['email'] = user.email

        return token

class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'