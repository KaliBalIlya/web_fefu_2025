from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from fefu_lab.models import Student, Instructor, UserProfile
from datetime import date

class Command(BaseCommand):
    help = 'Мигрирует существующие данные для новой системы аутентификации'
    
    def handle(self, *args, **options):
        self.stdout.write('Миграция данных аутентификации...')
        
        # Мигрируем студентов
        students_without_user = Student.objects.filter(user__isnull=True)
        for student in students_without_user:
            # Создаем пользователя на основе email студента
            email = getattr(student, 'email', None)
            if not email:
                # Если email нет в старой модели, генерируем
                email = f"student{student.id}@fefu.ru"
            
            username = f"student_{student.id}"
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'first_name': 'Студент',  # Заглушка
                    'last_name': f'#{student.id}',
                }
            )
            if created:
                user.set_password('temp_password_123')
                user.save()
            
            # Связываем студента с пользователем
            student.user = user
            student.save()
            
            # Создаем профиль пользователя
            UserProfile.objects.get_or_create(
                user=user,
                defaults={'role': 'STUDENT'}
            )
            
            self.stdout.write(f'Мигрирован студент: {user.username}')
        
        # Мигрируем преподавателей
        instructors_without_user = Instructor.objects.filter(user__isnull=True)
        for instructor in instructors_without_user:
            # Создаем пользователя
            email = getattr(instructor, 'email', None)
            if not email:
                email = f"instructor{instructor.id}@fefu.ru"
            
            username = f"instructor_{instructor.id}"
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'first_name': 'Преподаватель',  # Заглушка
                    'last_name': f'#{instructor.id}',
                }
            )
            if created:
                user.set_password('temp_password_123')
                user.save()
            
            # Связываем преподавателя с пользователем
            instructor.user = user
            instructor.save()
            
            # Создаем профиль пользователя
            UserProfile.objects.get_or_create(
                user=user,
                defaults={'role': 'TEACHER'}
            )
            
            self.stdout.write(f'Мигрирован преподаватель: {user.username}')
        
        self.stdout.write(
            self.style.SUCCESS('Миграция данных завершена успешно!')
        )
