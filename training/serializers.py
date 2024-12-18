from rest_framework import serializers
from training.models import Course, Profile, CourseEmployee


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = '__all__'


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = '__all__'


class CourseEmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseEmployee
        fields = '__all__'
