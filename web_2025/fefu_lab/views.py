from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, Http404
from django.views import View
from django.views.generic import ListView, DetailView
from django.db.models import Count
from .models import Student, Course, Instructor, Enrollment
from .forms import FeedbackForm, StudentRegistrationForm, EnrollmentForm

# ---------- Главная страница ----------
def home_page(request):
    total_students = Student.objects.filter(is_active=True).count()
    total_courses = Course.objects.filter(is_active=True).count()
    total_instructors = Instructor.objects.filter(is_active=True).count()
    recent_courses = Course.objects.filter(is_active=True).order_by('-created_at')[:3]
    
    return render(request, 'fefu_lab/home.html', {
        'total_students': total_students,
        'total_courses': total_courses,
        'total_instructors': total_instructors,
        'recent_courses': recent_courses,
    })

# ---------- О нас ----------
class AboutPage(View):
    def get(self, request):
        return render(request, 'fefu_lab/about.html')

# ---------- Список студентов ----------
class StudentListView(ListView):
    model = Student
    template_name = 'fefu_lab/student_list.html'
    context_object_name = 'students'
    
    def get_queryset(self):
        return Student.objects.filter(is_active=True).select_related()

# ---------- Детальная страница студента ----------
class StudentDetailView(DetailView):
    model = Student
    template_name = 'fefu_lab/student_detail.html'
    context_object_name = 'student'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = self.get_object()
        context['enrollments'] = student.enrollments.select_related('course')
        return context

# ---------- Список курсов ----------
class CourseListView(ListView):
    model = Course
    template_name = 'fefu_lab/course_list.html'
    context_object_name = 'courses'
    
    def get_queryset(self):
        return Course.objects.filter(is_active=True).select_related('instructor')

# ---------- Детальная страница курса ----------
class CourseDetailView(DetailView):
    model = Course
    template_name = 'fefu_lab/course_detail.html'
    context_object_name = 'course'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = self.get_object()
        context['enrollments'] = course.enrollments.select_related('student')
        context['available_slots'] = course.max_students - course.enrolled_students_count
        return context

# ---------- Форма обратной связи ----------
def feedback_view(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
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

# ---------- Регистрация студента ----------
def register_view(request):
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            student = form.save()
            return render(request, 'fefu_lab/success.html', {
                'message': f'Студент {student.full_name} успешно зарегистрирован!',
                'title': 'Регистрация'
            })
    else:
        form = StudentRegistrationForm()
    
    return render(request, 'fefu_lab/register.html', {
        'form': form,
        'title': 'Регистрация студента'
    })

# ---------- Запись на курс ----------
def enrollment_view(request):
    if request.method == 'POST':
        form = EnrollmentForm(request.POST)
        if form.is_valid():
            enrollment = form.save(commit=False)
            # В реальном приложении здесь бы была логика привязки к текущему студенту
            enrollment.save()
            return render(request, 'fefu_lab/success.html', {
                'message': f'Вы успешно записаны на курс "{enrollment.course.title}"!',
                'title': 'Запись на курс'
            })
    else:
        form = EnrollmentForm()
    
    return render(request, 'fefu_lab/enrollment.html', {
        'form': form,
        'title': 'Запись на курс'
    })

# ---------- Обработчик 404 ----------
def page_not_found(request, exception):
    return render(request, 'fefu_lab/404.html', status=404)
