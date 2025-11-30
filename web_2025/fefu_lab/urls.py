from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Существующие маршруты
    path('', views.home_page, name='home'),
    path('about/', views.AboutPage.as_view(), name='about'),
    path('students/', views.StudentListView.as_view(), name='student_list'),
    path('student/<int:pk>/', views.student_detail, name='student_detail'),
    path('courses/', views.CourseListView.as_view(), name='course_list'),
    path('course/<slug:slug>/', views.CourseDetailView.as_view(), name='course_detail'),
    path('feedback/', views.feedback_view, name='feedback'),
    path('enrollment/', views.enrollment_view, name='enrollment'),
    
    # Новые маршруты аутентификации
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit_view, name='profile_edit'),
    
    # Личные кабинеты
    path('dashboard/student/', views.student_dashboard, name='student_dashboard'),
    path('dashboard/teacher/', views.teacher_dashboard, name='teacher_dashboard'),
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
]

handler404 = 'fefu_lab.views.page_not_found'
