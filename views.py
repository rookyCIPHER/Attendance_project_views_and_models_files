from django.shortcuts import render, HttpResponse
from home.models import attendance_record_table, session_record_table, person_table, course_table
import simplejson as json

# Create your views here.


#########  Errors are not specified if a query is made and it is not available, might have to add them ###########################
######### whenever using list() to directly convert the list of queries to a proper list data structure use .filter() as .get() won't work. However to access attributes of queries such as .date or .name only get() can be used to access them ###################

# creates new session for the course and returns status confirmation
def create_new_session(request):
    if request.method == "POST":

        # creating database entry
        course_name = request.POST['course_name']
        date = request.POST['session_date']
        start_time = request.POST['session_start_time']
        end_time = request.POST['session_end_time']
        location = request.POST['location']

        ins = session_record_table(course_name=course_name, date=date,
                                   start_time=start_time, end_time=end_time, location=location)
        ins.save()

        # getting session id
        session_id = session_record_table.objects.filter(
            course_name=course_name, date=date, start_time=start_time, end_time=end_time, location=location).values('id')[0]['id']

        print(session_id)

        # storing the id in the courses entry
        course = course_table.objects.get(name=course_name)
        jsonDec = json.decoder.JSONDecoder()
        session_records = jsonDec.decode(course.sessions_list)
        session_records.append(session_id)

        course.sessions_list = json.dumps(session_records)
        course.save()

    return render(request, 'create.html')


# marks attendance of students and returns status confirmation
def mark_attendance(request):
    if request.method == "POST":
        rollNumber = request.POST['rollNumber']
        course_name = request.POST['course_name']
        jsonDec = json.decoder.JSONDecoder()
        course_sessions_list = jsonDec.decode(course_table.objects.get(
            name=course_name).sessions_list)
        session_id = course_sessions_list[len(course_sessions_list)-1]

        ins = attendance_record_table(
            student_id=rollNumber, course_name=course_name, session=session_id)

        ins.save()
    return render(request, 'attendance.html')


# registers a student for the course and returns status confirmation
def course_registration(request):
    if request.method == "POST":

        # getting the verification code that the student entered
        student_id = request.POST['student_id']
        verification_code_entered = request.POST['verification_code_entered']

        # checking validity of the code
        courses_list = course_table.objects.all()
        flag = 0

        for course in courses_list:
            if (verification_code_entered == course.verification_code):
                flag = 1

                # adding the course to student profile
                course = course_table.objects.filter(
                    verification_code=verification_code_entered)
                course_id = course.values('id')[0]['id']
                student = person_table.objects.get(rollNumber=student_id)

                jsonDec = json.decoder.JSONDecoder()
                course_records = jsonDec.decode(student.courses_list)
                course_records.append(course_id)
                student.courses_list = json.dumps(course_records)
                student.save()

                # adding the student to course profile
                course_registered = course_table.objects.get(
                    verification_code=verification_code_entered)

                # we need to get the object again with .get because .filter won't allow us to use student_list

                students_records = jsonDec.decode(
                    course_registered.students_list)

                student_model = person_table.objects.filter(
                    rollNumber=student_id)

                student_model_id = student_model.values('id')[0]['id']

                students_records.append(student_model_id)

                course_registered.students_list = json.dumps(students_records)
                course_registered.save()

        if (flag == 0):
            print("Invalid Verification Code")
    return render(request, 'index.html')


# allows the teacher to create a new course and returns a status confirmation
def create_new_course(request):
    if request.method == "POST":
        name = request.POST['course_name']
        # generate random code
        verification_code = request.POST['verification_code']
        teacher = request.POST['teacher']
        students_list = []
        sessions_list = []

        ins = course_table(name=name, verification_code=verification_code, teacher=teacher,
                           students_list=json.dumps(students_list), sessions_list=json.dumps(sessions_list))

        ins.save()

    return render(request, 'course.html')


def new_student(request):  # registers a new student and returns status confirmation
    if request.method == "POST":
        name = request.POST['student_name']
        email = request.POST['student_email']
        isStudent = request.POST['isStudent']
        rollNumber = request.POST['rollNumber']
        courses_list = []

        ins = person_table(name=name, email=email, isStudent=isStudent,
                           rollNumber=rollNumber, courses_list=json.dumps(courses_list))

        ins.save()

    return render(request, 'student.html')


# to return list of sessions when a course tile is clicked
def course_session_details_teacher(request):
    sessions_list = []
    if request.method == "POST":
        # assuming we get course_name with the get request
        course_name = request.POST['course_name']
        jsonDec = json.decoder.JSONDecoder()
        course_sessions_list = jsonDec.decode(course_table.objects.get(
            name=course_name).sessions_list)

        for i in course_sessions_list:
            sessions_list.append(session_record_table.objects.get(id=i))

    return render(request, 'course_details_teacher.html', {'sessions': sessions_list})


# to display number of students present and total number of students
def session_attendance_stats(request):
    if request.method == "POST":
        # assuming we get course_name and session details with the get request

        course_name = request.POST['course_name']
        date = request.POST['date']
        start_time = request.POST['start_time']
        end_time = request.POST['end_time']

        session = session_record_table.objects.filter(
            course_name=course_name, date=date, start_time=start_time, end_time=end_time)

        session_id = session.values('id')[0]['id']

        # getting number of students present
        students_marked = len(list(attendance_record_table.objects.filter(
            course_name=course_name, session=session_id)))

        # getting total number of students in the course
        jsonDec = json.decoder.JSONDecoder()
        course = course_table.objects.get(name=course_name)
        total_students = len(jsonDec.decode(course.students_list))

        return [students_marked, total_students]


# returns the students present in the specified session
def session_attendance_list(request):
    students_marked = []
    if request.method == "POST":
        course_name = request.POST['course_name']
        date = request.POST['date']
        start_time = request.POST['start_time']
        end_time = request.POST['end_time']
        session = session_record_table.objects.filter(
            course_name=course_name, date=date, start_time=start_time, end_time=end_time)

        session_id = session.values('id')[0]['id']

        students_marked = list(attendance_record_table.objects.filter(
            course_name=course_name, session=session_id))

    return render(request, 'session_attendance_list.html', {'attendance': students_marked})


# returns the session the student was present in and the total sessions that have actually happened for the course, can also be used to show teacher data under the student filter
def course_session_details_student(request):
    present_sessions = []
    sessions_list = []
    if request.method == "POST":
        course_name = request.POST['course_name']
        student_id = request.POST['student_id']

        present_sessions_data = list(attendance_record_table.objects.filter(
            course_name=course_name, student_id=student_id))  # gives a list of session id

        for i in present_sessions_data:
            present_sessions.append(
                session_record_table.objects.get(id=i.session))

        jsonDec = json.decoder.JSONDecoder()
        course_sessions_list = jsonDec.decode(course_table.objects.get(
            name=course_name).sessions_list)

        for i in course_sessions_list:
            sessions_list.append(session_record_table.objects.get(id=i))

    return render(request, 'course_details_student.html', {'present': present_sessions, 'total': sessions_list})


# allows teacher to manually make changes to the attendance list and returns status confirmation
def edit_attendance_list(request):
    if request.method == "POST":
        course_name = request.POST['course_name']
        student_id = request.POST['student_id']
        date = request.POST['date']
        start_time = request.POST['start_time']
        end_time = request.POST['end_time']

        session = session_record_table.objects.filter(
            course_name=course_name, date=date, start_time=start_time, end_time=end_time)

        session_id = session.values('id')[0]['id']

        ins = attendance_record_table(
            student_id=student_id, course_name=course_name, session=session_id)

        ins.save()


# editing student details once with admin permission
