from django.http import HttpResponse, Http404
from django.views import View
from django.views.generic import TemplateView


# ---------- Function-Based View для главной страницы ----------
def home_page(request):
    html = """
    <html>
    <head><title>Главная</title></head>
    <body>
        <h1>Добро пожаловать на главную страницу!</h1>
        <p>Это простое Django-приложение для лабораторной работы №1.</p>
        <nav>
            <a href="/">Главная</a> |
            <a href="/about/">О нас</a> |
            <a href="/student/1/">Студент 1</a> |
            <a href="/course/python-basics/">Курс Python Basics</a>
        </nav>
    </body>
    </html>
    """
    return HttpResponse(html)


# ---------- Class-Based View для "О нас" ----------
class AboutPage(TemplateView):
    def get(self, request):
        html = """
        <html>
        <head><title>О нас</title></head>
        <body>
            <h1>О нашем приложении</h1>
            <p>Это приложение создано в рамках курса по Django.</p>
            <p>Мы изучаем маршрутизацию и представления (Views).</p>
            <a href="/">На главную</a>
        </body>
        </html>
        """
        return HttpResponse(html)


# ---------- Function-Based View для профиля студента ----------
def student_profile(request, student_id):
    # проверим, существует ли "студент"
    if student_id < 1 or student_id > 100:
        raise Http404("Студент не найден")

    html = f"""
    <html>
    <head><title>Профиль студента</title></head>
    <body>
        <h1>Профиль студента #{student_id}</h1>
        <ul>
            <li>ID: {student_id}</li>
            <li>Группа: ИВТ-01</li>
        </ul>
        <a href="/">Назад</a>
    </body>
    </html>
    """
    return HttpResponse(html)


# ---------- Class-Based View для курса по slug ----------
class CourseView(View):
    def get(self, request, course_slug):
        valid_slugs = ["python-basics", "web-development", "algorithms"]
        if course_slug not in valid_slugs:
            raise Http404("Курс не найден")

        html = f"""
        <html>
        <head><title>Курс {course_slug}</title></head>
        <body>
            <h1>Курс: {course_slug.replace('-', ' ').title()}</h1>
            <p>Это описание курса <b>{course_slug}</b>.</p>
            <a href="/">На главную</a>
        </body>
        </html>
        """
        return HttpResponse(html)


# ---------- Обработчик 404 (кастомная страница) ----------
def page_not_found(request, exception):
    html = """
    <html>
    <head><title>404 - Страница не найдена</title></head>
    <body>
        <h1>Ошибка 404</h1>
        <p>К сожалению, страница не найдена.</p>
        <a href="/">Вернуться на главную</a>
    </body>
    </html>
    """
    return HttpResponse(html, status=404)

