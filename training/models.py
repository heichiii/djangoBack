from django.contrib.auth.models import User
from django.db import models


# table
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    id = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=50)
    department = models.CharField(max_length=50)
    position = models.CharField(max_length=50)
    phone = models.CharField(max_length=15)
    role = models.CharField(max_length=50, default='employee')


class Course(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=50)
    date = models.DateField()
    trainer_id = models.CharField(max_length=50)
    content_url = models.URLField()
    department = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class CourseEmployee(models.Model):
    course_id = models.CharField(max_length=50)
    employee_id = models.CharField(max_length=50)
    grade = models.IntegerField()


# view
class PublishedCourse(models.Model):
    course_id = models.CharField(max_length=50,primary_key=True)
    name = models.CharField(max_length=50)
    date = models.DateField()
    trainer_id = models.CharField(max_length=50)
    content_url = models.URLField()
    department = models.CharField(max_length=50)
    stcnt = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'published_courses'


# Create your models here.
