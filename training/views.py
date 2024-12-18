from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from .models import Course, Profile, CourseEmployee, PublishedCourse
from django.http import HttpResponse, JsonResponse
import json
import jwt
from datetime import datetime, timedelta
from django.views.decorators.csrf import csrf_exempt


#   token
def generate_jwt_token(user):
    payload = {
        'user_id': user.id,
        'exp': datetime.utcnow() + timedelta(days=1),  # 过期时间为 1 天
        'iat': datetime.utcnow(),
    }
    token = jwt.encode(payload, 'your-secret-key', algorithm='HS256')
    return token


def validate_jwt_token(token):
    try:
        payload = jwt.decode(token, 'your-secret-key', algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None  # Token 过期
    except jwt.InvalidTokenError:
        return None  # Token 无效


# common
@csrf_exempt
def login(request):
    if request.method == 'POST':

        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        role = data.get('role')

        # 验证用户信息
        user = authenticate(request, username=username, password=password)
        if user:
            # 生成 token
            token = generate_jwt_token(user)
            print('normal login')
            return JsonResponse({
                'code': 200,
                'data': {
                    'token': token
                },
                'message': 'success'
            })
        else:
            return JsonResponse({
                'code': 401,
                'data': None,
                'message': 'error',
                'content': 'Invalid username or password'
            })
    else:
        return JsonResponse({
            'code': 405,
            'data': None,
            'message': 'error',
            'content': 'Method not allowed'
        })


@csrf_exempt
def get_user_info_view(request):
    if request.method == 'GET':
        token = request.META.get('HTTP_TOKEN')  # 从请求头部获取 token
        if token:
            payload = validate_jwt_token(token)
            if payload:
                user_id = payload.get('user_id')
                # profile = Profile.objects.get(id=user_id)
                try:
                    user = User.objects.get(id=user_id)
                    user_info = {
                        'username': user.username,
                        'email': user.email,
                        'id': user.profile.id,
                        'name': user.profile.name,
                        'department': user.profile.department,
                        'position': user.profile.position,
                        'phone': user.profile.phone,
                        'role': user.profile.role,
                        'isLogin': True

                        # 可以添加更多用户信息
                    }
                    return JsonResponse({
                        'code': 200,
                        'data': user_info,
                        'message': 'success'
                    })
                except User.DoesNotExist:
                    return JsonResponse({
                        'code': 404,
                        'data': None,
                        'message': 'error',
                        'content': 'User not found'
                    })
            else:
                return JsonResponse({
                    'code': 401,
                    'data': None,
                    'message': 'error',
                    'content': 'Invalid or expired token'
                })
        else:
            return JsonResponse({
                'code': 403,
                'data': None,
                'message': 'error',
                'content': 'No token provided'
            })
    else:
        return JsonResponse({
            'code': 405,
            'data': None,
            'message': 'error',
            'content': 'Method not allowed'
        })


def update_user_info(request):
    if request.method == 'POST':
        token = request.META.get('HTTP_TOKEN')
        data = json.loads(request.body)
        if token:
            payload = validate_jwt_token(token)
            if payload:
                user_id = payload.get('user_id')
                user = User.objects.get(id=user_id)
                profile = Profile.objects.get(user=user)

                username = data.get('username')
                if username != user.username and User.objects.filter(username=username).exists():
                    return JsonResponse({'message': 'existed'}, status=400)

                user.username = username
                user.email = data.get('email')
                user.save()
                profile.id = data.get('id')
                profile.name = data.get('name')
                profile.department = data.get('department')
                profile.position = data.get('position')
                profile.phone = data.get('phone')
                profile.role = data.get('role')
                profile.save()
                return JsonResponse({'message': 'success', 'code': 200})
            else:
                return JsonResponse({'message': 'error'})
        else:
            return JsonResponse({'message': 'error'})


def update_password(request):
    if request.method == 'POST':
        token = request.META.get('HTTP_TOKEN')
        data = json.loads(request.body)
        original_password = data.get('current_password')
        new_password = data.get('new_password')
        if token:
            payload = validate_jwt_token(token)
            if payload:
                user_id = payload.get('user_id')
                user = User.objects.get(id=user_id)
                print(user.check_password(original_password))
                if user.check_password(original_password):
                    user.set_password(new_password)
                    user.save()
                    return JsonResponse({'message': 'success', 'code': 200})
            else:
                return JsonResponse({'message': 'error', 'code': 401})
        else:
            return JsonResponse({'message': 'error', 'code': 403})
    return JsonResponse({'message': 'error', 'code': 405})


def register(request):
    if request.method == 'POST':
        role = request.POST.get('role')
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        if User.objects.filter(username=username).exists():
            return JsonResponse({'message': 'existed'}, status=400)
        if role == 'manager':
            user = User.objects.create_superuser(username=username, password=password, email=email)
        else:
            user = User.objects.create_user(username=username, password=password, email=email)

        id = request.POST.get('id')
        name = request.POST.get('name')
        department = request.POST.get('department')
        position = request.POST.get('position')
        phone = request.POST.get('phone')
        profile = Profile.objects.create(user=user, id=id, name=name, department=department, position=position,
                                         phone=phone, role=role)
        return JsonResponse({'message': 'success', 'user': profile.id})


# employee
def get_accessible_courses(request):
    if request.method == 'GET':
        token = request.META.get('HTTP_TOKEN')
        if token:
            payload = validate_jwt_token(token)
            if payload:
                user_id = payload.get('user_id')
                user = User.objects.get(id=user_id)
                profile = Profile.objects.get(user=user)
                if profile.role == 'employee':
                    courses = Course.objects.filter(department=profile.department)
                    data = []
                    for course in courses:
                        data.append(
                            {'id': course.id, 'name': course.name, 'date': course.date, 'trainer_id': course.trainer_id,
                             'content_url': course.content_url, 'department': course.department})

                    result = {'code': 200, 'data': data, 'message': 'success'}
                    return JsonResponse(result, safe=False)


def select_course(request):
    if request.method == 'GET':
        token = request.META.get('HTTP_TOKEN')
        if token:
            payload = validate_jwt_token(token)
            if payload:
                user_id = payload.get('user_id')
                user = User.objects.get(id=user_id)
                profile = Profile.objects.get(user=user)
                if profile.role == 'employee':
                    action = request.GET.get('action')
                    courseName = request.GET.get('courseName')
                    uid = profile.id
                    if action == 'select':
                        course = Course.objects.get(name=courseName)
                        CourseEmployee.objects.create(course_id=course.id, employee_id=uid)
                        return JsonResponse({'message': 'success', 'code': 200})
                    elif action == 'cancel':
                        course = Course.objects.get(name=courseName)
                        CourseEmployee.objects.filter(course_id=course.id, employee_id=uid).delete()
                        return JsonResponse({'message': 'success', 'code': 200})
                    else:
                        return JsonResponse({'message': 'error', 'code': 400})


def get_selected_courses(request):
    if request.method == 'GET':
        token = request.META.get('HTTP_TOKEN')
        if token:
            payload = validate_jwt_token(token)
            if payload:
                user_id = payload.get('user_id')
                user = User.objects.get(id=user_id)
                profile = Profile.objects.get(user=user)
                if profile.role == 'employee':
                    courses = CourseEmployee.objects.filter(employee_id=profile.id)
                    data = []
                    for course in courses:
                        course = Course.objects.get(id=course.course_id)
                        data.append(
                            {'id': course.id, 'name': course.name, 'date': course.date, 'trainer_id': course.trainer_id,
                             'content_url': course.content_url, 'department': course.department})
                    result = {'code': 200, 'data': data, 'message': 'success'}
                    return JsonResponse(result, safe=False)


# trainer
def get_published_courses(request):
    if request.method == 'GET':
        token = request.META.get('HTTP_TOKEN')
        if token:
            payload = validate_jwt_token(token)
            if payload:
                user_id = payload.get('user_id')
                user = User.objects.get(id=user_id)
                profile = Profile.objects.get(user=user)
                if profile.role == 'trainer':
                    courses = PublishedCourse.objects.filter(trainer_id=profile.id)

                    data = []
                    for course in courses:
                        data.append({'id': course.course_id, 'name': course.name, 'date': course.date,
                                     'content_url': course.content_url,
                                     'department': course.department, 'stcnt': course.stcnt})
                    result = {'code': 200, 'data': data, 'message': 'success'}
                    return JsonResponse(result, safe=False)


def publish_course(request):
    if request.method == 'POST':
        token = request.META.get('HTTP_TOKEN')
        data = json.loads(request.body)
        if token:
            payload = validate_jwt_token(token)
            if payload:
                user_id = payload.get('user_id')
                user = User.objects.get(id=user_id)
                profile = Profile.objects.get(user=user)
                if profile.role == 'trainer':
                    id = data.get('id')
                    name = data.get('name')
                    date = data.get('date')
                    trainer_id = profile.id
                    content_url = data.get('content_url')
                    department = data.get('department')

                    course = Course.objects.create(id=id, name=name, date=date,
                                                   trainer_id=trainer_id, content_url=content_url,
                                                   department=department)
                    return JsonResponse({'message': 'success', 'code': 200})
            else:
                return JsonResponse({'message': 'error', 'code': 401})
        else:
            return JsonResponse({'message': 'error', 'code': 403})


def get_users(request):
    if request.method == 'GET':
        users = Profile.objects.all()
        data = []
        for user in users:
            data.append({'id': user.id, 'name': user.name, 'department': user.department, 'position': user.position,
                         'phone': user.phone, 'role': user.role})
        return JsonResponse(data, safe=False)


def get_managers(request):
    if request.method == 'GET':
        managers = Profile.objects.filter(role='manager')
        data = []
        for manager in managers:
            data.append(
                {'id': manager.id, 'name': manager.name, 'department': manager.department, 'position': manager.position,
                 'phone': manager.phone, 'role': manager.role})
        return JsonResponse(data, safe=False)


def get_employees(request):
    if request.method == 'GET':
        employees = Profile.objects.filter(role='employee')
        data = []
        for employee in employees:
            data.append({'id': employee.id, 'name': employee.name, 'department': employee.department,
                         'position': employee.position,
                         'phone': employee.phone, 'role': employee.role})
        return JsonResponse(data, safe=False)


def get_trainers(request):
    if request.method == 'GET':
        trainers = Profile.objects.filter(role='trainer')
        data = []
        for trainer in trainers:
            data.append(
                {'id': trainer.id, 'name': trainer.name, 'department': trainer.department, 'position': trainer.position,
                 'phone': trainer.phone, 'role': trainer.role})
        return JsonResponse(data, safe=False)


def get_courses(request):
    if request.method == 'GET':
        courses = Course.objects.all()
        data = []
        for course in courses:
            data.append({'id': course.id, 'name': course.name, 'date': course.date, 'trainer_id': course.trainer_id,
                         'content_url': course.content_url, 'department': course.department})

        return JsonResponse(data, safe=False)


def get_course(request, course_id):
    if request.method == 'GET':
        course = Course.objects.get(id=course_id)
        return JsonResponse({'id': course.id, 'name': course.name, 'date': course.date, 'trainer_id': course.trainer_id,
                             'content_url': course.content_url, 'department': course.department})
