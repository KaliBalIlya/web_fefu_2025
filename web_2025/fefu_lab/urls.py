from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_page, name='home'),
    path('about/', views.AboutPage.as_view(), name='about'),
    path('student/<int:student_id>/', views.student_profile, name='student'),
    path('course/<slug:course_slug>/', views.CourseView.as_view(), name='course'),
]

# обработчик 404
handler404 = 'fefu_lab.views.page_not_found'
