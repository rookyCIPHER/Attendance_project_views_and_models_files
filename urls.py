from django.contrib import admin
from django.urls import path, include
import os
from home import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.course_registration, name='home'),
    path('create', views.create_new_session, name='created'),
    path('course', views.create_new_course, name="course"),
    path('student', views.new_student, name="student"),
    path('attendance', views.mark_attendance, name="attendance"),
    path('course_details_teacher',
         views.course_session_details_teacher, name="session_teacher"),

    path('session_attendance_details',
         views.session_attendance_list, name="attendance_list"),
    path('course_details_student',
         views.course_session_details_student, name="session_student")

]
