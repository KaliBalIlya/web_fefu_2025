from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, Http404
from django.views import View
from django.views.generic import ListView, DetailView
from django.db.models import Count
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Student, Course, Instructor, Enrollment, UserProfile
from .forms import FeedbackForm, CustomUserCreationForm, LoginForm, ProfileUpdateForm, UserProfileUpdateForm, StudentProfileUpdateForm, EnrollmentForm

# Декораторы для проверки ролей
def student_required(function=None):
    actual_decorator = user_passes_test(
        lambda u: hasattr(u, 'profile') and u.profile.role == 'STUDENT',
        login_url='/login/'
    )
    if function:
        return actual_decorator(function)
    return actual_decorator

def teacher_required(function=None):
    actual_decorator = user_passes_test(
        lambda u: hasattr(u, 'profile') and u.profile.role == 'TEACHER',
        login_url='/login/'
    )
    if function:
        return actual_decorator(function)
    return actual_decorator

def admin_required(function=None):
    actual_decorator = user_passes_test(
        lambda u: hasattr(u, 'profile') and u.profile.role == 'ADMIN',
        login_url='/login/'
    )
    if function:
        return actual_decorator(function)
    return actual_decorator

# ---------- Главная страница ----------
def home_page(request):
    total_students = Student.objects.filter(is_active=True).count()
    total_courses = Course.objects.filter(is_active=True).count()
    total_instructors = Instructor.objects.filter(is_active=True).count()
    recent_courses = Course.objects.filter(is_active=True).order_by('-created_at')[:3]
    
    context = {
        'total_students': total_students,
        'total_courses': total_courses,
        'total_instructors': total_instructors,
        'recent_courses': recent_courses,
    }
    
    # Добавляем информацию о пользователе, если он авторизован
    if request.user.is_authenticated:
        context['user_profile'] = getattr(request.user, 'profile', None)
    
    return render(request, 'fefu_lab/home.html', context)

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
        return Student.objects.filter(is_active=True).select_related('user')

# ---------- Детальная страница студента ----------
def student_detail(request, pk):
    student = get_object_or_404(Student, pk=pk)
    enrollments = Enrollment.objects.filter(student=student).select_related('course')
    
    context = {
        'student': student,
        'enrollments': enrollments,
    }
    return render(request, 'fefu_lab/student_detail.html', context)

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

# ---------- Регистрация ----------
def register_view(request):
    if request.user.is_authenticated:
        return redirect('profile')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Явно указываем бэкенд для логина
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)
            
            messages.success(request, f'Аккаунт создан для {user.get_full_name()}!')
            return redirect('profile')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'fefu_lab/registration/register.html', {
        'form': form,
        'title': 'Регистрация'
    })

# ---------- Вход ----------
def login_view(request):
    if request.user.is_authenticated:
        return redirect('profile')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                # Явно указываем бэкенд
                user.backend = 'django.contrib.auth.backends.ModelBackend'
                login(request, user)
                messages.success(request, f'Добро пожаловать, {user.get_full_name()}!')
                next_url = request.GET.get('next', 'profile')
                return redirect(next_url)
            else:
                messages.error(request, 'Неверные учетные данные. Попробуйте снова.')
    else:
        form = LoginForm()
    
    return render(request, 'fefu_lab/registration/login.html', {'form': form})
# ---------- Выход ----------
def logout_view(request):
    logout(request)
    messages.success(request, 'Вы успешно вышли из системы.')
    return redirect('home')

# ---------- Профиль ----------
@login_required
def profile_view(request):
    user = request.user
    context = {
        'user': user,
    }
    
    # Добавляем данные в зависимости от роли
    if hasattr(user, 'profile'):
        if user.profile.role == 'STUDENT' and hasattr(user, 'student_profile'):
            context['student'] = user.student_profile
            context['enrollments'] = Enrollment.objects.filter(student=user.student_profile)
        elif user.profile.role == 'TEACHER' and hasattr(user, 'instructor_profile'):
            context['instructor'] = user.instructor_profile
            context['courses'] = Course.objects.filter(instructor=user.instructor_profile)
    
    return render(request, 'fefu_lab/registration/profile.html', context)

# ---------- Редактирование профиля ----------
@login_required
def profile_edit_view(request):
    user = request.user
    
    if request.method == 'POST':
        user_form = ProfileUpdateForm(request.POST, instance=user)
        profile_form = UserProfileUpdateForm(request.POST, request.FILES, instance=user.profile)
        
        # Формы для конкретных ролей
        student_form = None
        if hasattr(user, 'student_profile'):
            student_form = StudentProfileUpdateForm(request.POST, instance=user.student_profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            
            if student_form and student_form.is_valid():
                student_form.save()
            
            messages.success(request, 'Профиль успешно обновлен!')
            return redirect('profile')
    else:
        user_form = ProfileUpdateForm(instance=user)
        profile_form = UserProfileUpdateForm(instance=user.profile)
        student_form = None
        
        if hasattr(user, 'student_profile'):
            student_form = StudentProfileUpdateForm(instance=user.student_profile)
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'student_form': student_form,
    }
    
    return render(request, 'fefu_lab/registration/profile_edit.html', context)

# ---------- Запись на курс ----------
@login_required
@student_required
def enrollment_view(request):
    if request.method == 'POST':
        form = EnrollmentForm(request.POST)
        if form.is_valid():
            enrollment = form.save(commit=False)
            # Устанавливаем текущего студента
            enrollment.student = request.user.student_profile
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

# ---------- Личные кабинеты ----------
@login_required
@student_required
def student_dashboard(request):
    student = get_object_or_404(Student, user=request.user)
    enrollments = Enrollment.objects.filter(student=student).select_related('course')
    
    context = {
        'student': student,
        'enrollments': enrollments,
    }
    return render(request, 'fefu_lab/dashboard/student_dashboard.html', context)

@login_required
@teacher_required
def teacher_dashboard(request):
    instructor = get_object_or_404(Instructor, user=request.user)
    courses = Course.objects.filter(instructor=instructor)
    
    # Статистика по курсам
    course_stats = []
    for course in courses:
        enrollments_count = Enrollment.objects.filter(course=course, status='ACTIVE').count()
        course_stats.append({
            'course': course,
            'enrollments_count': enrollments_count,
            'available_slots': course.max_students - enrollments_count,
        })
    
    context = {
        'instructor': instructor,
        'course_stats': course_stats,
    }
    return render(request, 'fefu_lab/dashboard/teacher_dashboard.html', context)

@login_required
@admin_required
def admin_dashboard(request):
    # Статистика для администратора
    total_students = Student.objects.filter(is_active=True).count()
    total_teachers = Instructor.objects.filter(is_active=True).count()
    total_courses = Course.objects.filter(is_active=True).count()
    total_enrollments = Enrollment.objects.filter(status='ACTIVE').count()
    
    context = {
        'total_students': total_students,
        'total_teachers': total_teachers,
        'total_courses': total_courses,
        'total_enrollments': total_enrollments,
    }
    return render(request, 'fefu_lab/dashboard/admin_dashboard.html', context)

# ---------- Обработчик 404 ----------
def page_not_found(request, exception):
    return render(request, 'fefu_lab/404.html', status=404)
