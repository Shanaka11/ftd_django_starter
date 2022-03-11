# Python
# Django
from django.urls import path
# Rest Framework
# 3rd Party
# Local
from .api.userApi import Login, RefreshLogin, CreateUser, VerifyEmail, RemoveUser, UpdateUser, ChangePasswordRequest, ChangePassword, GetUser, GetUsers


urlpatterns = [
    path('token/', Login.as_view(), name='login'),
    path('token/refresh/', RefreshLogin.as_view(), name='refresh_login'),
    path('create_user/', CreateUser, name='register'),
    path('verify_email/<int:user_id>/<str:token>', VerifyEmail, name='verify_email'),
    path('remove/<int:user_id>', RemoveUser, name='remove_user'),
    path('update/<int:user_id>', UpdateUser, name='update_user'),
    path('change_password_req', ChangePasswordRequest, name='change_password_request'),
    path('change_password/<int:user_id>/<str:token>', ChangePassword, name='change_password'),
    path('', GetUsers, name='get_user_list'),
    path('<int:id>', GetUser, name='get_user')
]