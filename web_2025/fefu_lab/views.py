from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404
from django.views import View
from django.views.generic import TemplateView
from .forms import FeedbackForm, RegistrationForm
from .models import UserProfile

# Мок-данные для студентов и курсов
STUDENTS_DATA = {
    1: {
        'info': 'Иван Петров',
        'faculty': 'Кибербезопасность',
        'status': 'Активный',
        'year': 3
    },
    2: {
        'info': 'Мария Сидорова', 
        'faculty': 'Информатика',
        'status': 'Активный',
        'year': 2
    },
    3: {
        'info': 'Алексей Козлов',
        'faculty': 'Программная инженерия', 
        'status': 'Выпускник',
        'year': 5
    }
}

COURSES_DATA = {
    'python-basics': {
        'name': 'Основы программирования на Python',
        'duration': 36,
        'description': 'Базовый курс по программированию на языке Python для начинающих.',
        'instructor': 'Доцент Петров И.С.',
        'level': 'Начальный'
    },
    'web-security': {
        'name': 'Веб-безопасность',
        'duration': 48,
        'description': 'Курс по защите веб-приложений от современных угроз.',
        'instructor': 'Профессор Сидоров А.В.',
        'level': 'Продвинутый'
    },
    'network-defense': {
        'name': 'Защита сетей',
        'duration': 42,
        'description': 'Изучение методов и технологий защиты компьютерных сетей.',
        'instructor': 'Доцент Козлова М.П.',
        'level': 'Средний'
    }
}

# ---------- Function-Based View для главной страницы ----------
def home_page(request):
    return render(request, 'fefu_lab/home.html')

# ---------- Class-Based View для "О нас" ----------
class AboutPage(View):
    def get(self, request):
        return render(request, 'fefu_lab/about.html')

# ---------- Function-Based View для профиля студента ----------
def student_profile(request, student_id):
    if student_id in STUDENTS_DATA:
        student_data = STUDENTS_DATA[student_id]
        return render(request, 'fefu_lab/student_profile.html', {
            'student_id': student_id,
            'student_info': student_data['info'],
            'faculty': student_data['faculty'],
            'status': student_data['status'],
            'year': student_data['year']
        })
    else:
        raise Http404("Студент с таким ID не найден")

# ---------- Class-Based View для курса по slug ----------
class CourseView(View):
    def get(self, request, course_slug):
        if course_slug in COURSES_DATA:
            course_data = COURSES_DATA[course_slug]
            return render(request, 'fefu_lab/course_detail.html', {
                'course_slug': course_slug,
                'course_name': course_data['name'],
                'duration': course_data['duration'],
                'description': course_data['description'],
                'instructor': course_data['instructor'],
                'level': course_data['level']
            })
        else:
            raise Http404("Курс не найден")

# ---------- Форма обратной связи ----------
def feedback_view(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            # Здесь можно сохранить данные в базу или отправить email
            return render(request, 'fefu_lab/success.html', {
                'message': 'Спасибо за ваше сообщение! Мы свяжемся с вами в ближайшее время.',
                'title': 'Обратная связь'
            })
    else:
        form = FeedbackForm()
    
    return render(request, 'fefu_lab/feedback.html', {
        'form': form,
        'title': 'Обратная связь'
    })

# ---------- Форма регистрации ----------
def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            # Сохраняем пользователя в базу
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            
            user = UserProfile(username=username, email=email, password=password)
            user.save()
            
            return render(request, 'fefu_lab/success.html', {
                'message': f'Пользователь {username} успешно зарегистрирован!',
                'title': 'Регистрация'
            })
    else:
        form = RegistrationForm()
    
    return render(request, 'fefu_lab/register.html', {
        'form': form,
        'title': 'Регистрация'
    })

# ---------- Обработчик 404 (кастомная страница) ----------

def page_not_found(request, exception):
    html = """
    <html>
    <head><title>404 - Странича не найдeна</title></head>
    <body>
        <h1>Ошибка 404</h1>
        <р>К сожалению, страница не найдена.</p>
        <a href="/">Bернуться на главну</a>
    </body>
    </html>
    """
    return HttpResponse(html, status=404)
