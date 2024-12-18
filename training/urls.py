from django.urls import path
from .views import (login, get_user_info_view, update_user_info, update_password,
                    get_accessible_courses, select_course, get_selected_courses,get_published_courses,publish_course)

urlpatterns = [
    path('login', login, name='login'),
    path('profile', get_user_info_view, name='profile'),
    path('update_profile', update_user_info, name='update_profile'),
    path('update_password', update_password, name='update_password'),
    path('accessible_course', get_accessible_courses, name='courses'),
    path('select_course', select_course, name='select_course'),
    path('selected_course', get_selected_courses, name='selected_course'),
    path('published_course', get_published_courses, name='published_courses'),
    path('publish_course', publish_course, name='publish_course')
]
