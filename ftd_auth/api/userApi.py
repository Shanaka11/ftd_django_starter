# Python
import jwt
import datetime
import traceback
# Django
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth.models import User
from rest_framework import serializers
# from django.conf import settings
# from ..settings import api_settings as settings # App Specific Settings
from django.conf import settings as proj_settings # Project Specific Settings
from django.template.loader import render_to_string
from django.db import transaction
# Rest Framework
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAdminUser
# 3rd Party
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
# Local
from ..serializers.userSerializer import LoginSerializer, UserSerializer


class RefreshLogin(TokenRefreshView):
    pass

@permission_classes([AllowAny])
class Login(TokenObtainPairView):
    serializer_class = LoginSerializer

# Create User
@api_view(['POST'])
@permission_classes([AllowAny])
def CreateUser(request):
    data = request.data
    try:
        with transaction.atomic():
            if User.objects.filter(username=data['email']).exists():
                raise ValueError("An account exist with the same email")
            else:
                user = User.objects.create_user(data['email'], data['email'], data['password'])
                user.first_name = data['firstName']
                user.last_name = data['lastName']
                # Set active to true if no email validation is included
                user.is_active = False
                # Create the user Profile object as well
                user.save()
                # token = jwt.encode({'name': user.first_name, 'exp': datetime.datetime.now()}, settings.C_JWT_KEY, algorithm='HS256').decode()
                token = jwt.encode({'name': user.first_name, 'exp': datetime.datetime.now()}, proj_settings.SECRET_KEY, algorithm='HS256') 
                # This link Should direct to a frontend page and it will have a call to the bakcend to activate
                activation_link = proj_settings.C_CLIENT_URL + "/user/validate?id=" + str(user.id) + "&token=" + str(token)
                context = {
                    "name": user.first_name,
                    "link": activation_link
                }
                html_content = render_to_string("verify-email.html", context)

                msg = EmailMultiAlternatives('Auth Test', 'Auth Link', proj_settings.DEFAULT_FROM_EMAIL, [user.email])
                msg.attach_alternative(html_content, "text/html")
                # msg.send(fail_silently=True)

                return Response({"message": "User Created Successfully"}, status=201)
    except ValueError as e:
        print(traceback.format_exc())
        return Response({"message": str(e)}, status=400)
    except Exception as e:
        print(traceback.format_exc())
        return Response({"message": str(e)}, status=400)


# Verify EMail
"""
    When verifiying the link that is sent to the user should direct user to a page in the frontend application
    That page will invoke the below method to activate the user
     Handle user redirect after log in if the user has logged out for some reason
"""
@api_view(['GET'])
def VerifyEmail(request, user_id=None, token=None):

    try:
        byte_token = bytes(token, 'utf-8')
        decode_token = jwt.decode(byte_token, proj_settings.SECRET_KEY, algorithms='HS256')
        # if token is valid then do the activate the user
        if (datetime.datetime.now() - datetime.datetime.utcfromtimestamp(0)).total_seconds() - decode_token["exp"] <= proj_settings.C_JWT_TOKEN_EXP:
            user = User.objects.get(id=user_id)
            user.is_active = True
            user.save()
            return Response({"message": "Email Verified"}, status=201)
        else:
            return Response({"message": "Token is invalid"}, status=404)
    except Exception as e:
        return Response({"message": str(e)})

# Remove / Deactivate User
@api_view(['POST'])
@permission_classes([IsAdminUser])
def RemoveUser(request, user_id):
    try:
        user = User.objects.get(id=user_id)
        user.is_active = False
        user.save()
        return Response({'message': 'User Deactivated Successfully'}, status=201)
    except Exception as e:
        return Response({"message": str(e)})

# Edit User
@api_view(['PUT'])
def UpdateUser(request, user_id):
    try:
        data = request.data
        user = User.objects.get(id=user_id)
        user.first_name = data['firstName']
        user.last_name = data['lastName']
        user.save()
        return Response({'message': 'User Updated Successfully'}, status=201)
    except Exception as e:
        return Response({"message": str(e)})

# Change Password
"""
    When Changing the password through the user profile screen an email will be sent to the current email address
    containing a password reset link.
    If user has forgotten his password or wants to reset it then that same link will be sent to his email
    the link will contain a token and it will direct the user to a frontend page. The page prompt to change passwords
    and once submitted it will call the change password method
"""
@api_view(['POST'])
def ChangePassword(request, user_id, token):
    try:
        byte_token = bytes(token, 'utf-8')
        decode_token = jwt.decode(byte_token, proj_settings.SECRET_KEY, algorithms='HS256')
        # if token is valid then do the activate the user
        if (datetime.datetime.now() - datetime.datetime.utcfromtimestamp(0)).total_seconds() - decode_token["exp"] <= proj_settings.C_JWT_TOKEN_EXP:
            data = request.data
            if data['password'] != data['password2']:
                raise Exception('Passwords do not match')
            user = User.objects.get(id=user_id)
            user.set_password(data['password'])
            user.save()
        else:
            return Response({"message": "Token is invalid"}, status=404)
    except Exception as e:
        return Response({"message": str(e)})

# Password Reset / Forgotten Password
@api_view(['POST'])
def ChangePasswordRequest(request):
    try:
        data = request.data
        user = User.objects.get(email=data['email'])
        token = jwt.encode({'name': user.first_name, 'exp': datetime.datetime.now()}, proj_settings.SECRET_KEY, algorithm='HS256').decode() 
        activation_link = proj_settings.C_CLIENT_URL + "user/password_reset?id=" + str(user.id) + "&token=" + str(token)
        context = {
            "name": user.first_name,
            "link": activation_link
        }
        html_content = render_to_string("reset-password.html", context)
        msg = EmailMultiAlternatives('Reset Password', 'Reset Password', proj_settings.DEFAULT_FROM_EMAIL, [user.email])
        msg.attach_alternative(html_content, "text/html")
        # msg.send(fail_silently=True)
        return Response({"message": "Password Changed Successfully"}, status=201)
    except Exception as e:
        return Response({"message": str(e)})   

# Get User
@api_view(['GET'])
def GetUser(request, id):
    user = User.objects.get(id = id)
    serializer = UserSerializer(user)

    return Response(serializer.data)

# Get User List
@api_view(['GET'])
@permission_classes([IsAdminUser])
def GetUsers(request):
    users = User.objects.all()
    serializer = UserSerializer(users, many=True)

    return Response(serializer.data)