from django.contrib import admin
from .models import UserProfile, Student, Instructor, Course, Enrollment

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'phone', 'created_at']
    list_filter = ['role', 'created_at']
    search_fields = ['user__first_name', 'user__last_name', 'user__email', 'phone']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['user', 'faculty', 'is_active', 'created_at']
    list_filter = ['is_active', 'faculty', 'created_at']
    search_fields = ['user__first_name', 'user__last_name', 'user__email', 'student_id']
    list_editable = ['is_active']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = [
        ('Основная информация', {
            'fields': ['user', 'faculty', 'birth_date', 'student_id']
        }),
        ('Статус', {
            'fields': ['is_active']
        }),
        ('Даты', {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']
        }),
    ]

@admin.register(Instructor)
class InstructorAdmin(admin.ModelAdmin):
    list_display = ['user', 'specialization', 'is_active']
    list_filter = ['is_active', 'specialization']
    search_fields = ['user__first_name', 'user__last_name', 'user__email', 'specialization']
    list_editable = ['is_active']

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'instructor', 'level', 'duration', 'price', 'is_active', 'created_at']
    list_filter = ['is_active', 'level', 'instructor']
    search_fields = ['title', 'description']
    list_editable = ['is_active', 'price']
    prepopulated_fields = {'slug': ['title']}
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'enrolled_at', 'status', 'grade']
    list_filter = ['status', 'enrolled_at', 'course']
    search_fields = ['student__user__first_name', 'student__user__last_name', 'course__title']
    list_editable = ['status', 'grade']
    readonly_fields = ['enrolled_at']
