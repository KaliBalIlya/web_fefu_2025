from django import forms
from django.core.exceptions import ValidationError
from .models import UserProfile

class FeedbackForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        label='Имя',
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        error_messages={'required': 'Поле "Имя" обязательно для заполнения'}
    )
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
        error_messages={'required': 'Поле "Email" обязательно для заполнения'}
    )
    subject = forms.CharField(
        max_length=200,
        label='Тема сообщения',
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        error_messages={'required': 'Поле "Тема" обязательно для заполнения'}
    )
    message = forms.CharField(
        label='Текст сообщения',
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        error_messages={'required': 'Поле "Сообщение" обязательно для заполнения'}
    )

    def clean_name(self):
        name = self.cleaned_data['name']
        if len(name.strip()) < 2:
            raise ValidationError("Имя должно содержать минимум 2 символа")
        return name.strip()

    def clean_message(self):
        message = self.cleaned_data['message']
        if len(message.strip()) < 10:
            raise ValidationError("Сообщение должно содержать минимум 10 символов")
        return message.strip()

class RegistrationForm(forms.Form):
    username = forms.CharField(
        max_length=50,
        label='Логин',
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        error_messages={'required': 'Поле "Логин" обязательно для заполнения'}
    )
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
        error_messages={'required': 'Поле "Email" обязательно для заполнения'}
    )
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        error_messages={'required': 'Поле "Пароль" обязательно для заполнения'}
    )
    password_confirm = forms.CharField(
        label='Подтверждение пароля',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        error_messages={'required': 'Поле "Подтверждение пароля" обязательно для заполнения'}
    )

    def clean_username(self):
        username = self.cleaned_data['username']
        if UserProfile.objects.filter(username=username).exists():
            raise ValidationError("Пользователь с таким логином уже существует")
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        if UserProfile.objects.filter(email=email).exists():
            raise ValidationError("Пользователь с таким email уже существует")
        return email

    def clean_password(self):
        password = self.cleaned_data['password']
        if len(password) < 8:
            raise ValidationError("Пароль должен содержать минимум 8 символов")
        return password

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        
        if password and password_confirm and password != password_confirm:
            raise ValidationError("Пароли не совпадают")
        
        return cleaned_data
