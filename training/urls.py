from django.urls import path
from .views import register, login, get_profile, get_users, get_user_info_view

urlpatterns = [
    path('register', register, name='register'),
    path('login', login, name='login'),
    path('profile', get_user_info_view, name='profile'),
    path('users/', get_users, name='users')
]
