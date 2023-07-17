from django.db import models


# Create your models here.
class person_table(models.Model):
    name = models.TextField()
    email = models.EmailField()
    isStudent = models.BooleanField()
    rollNumber = models.IntegerField()
    courses_list = models.TextField(null=True)


class course_table(models.Model):
    name = models.CharField(max_length=50)
    verification_code = models.TextField()
    teacher = models.TextField()
    students_list = models.TextField(null=True)
    sessions_list = models.TextField(null=True)


class session_record_table(models.Model):
    course_name = models.CharField(max_length=50)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    location = models.TextField()


class attendance_record_table(models.Model):
    student_id = models.IntegerField()
    course_name = models.CharField(max_length=50)
    session = models.TextField()  # stores session id
