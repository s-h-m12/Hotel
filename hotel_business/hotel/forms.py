from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.exceptions import ValidationError
from .models import CustomUser, Guest, Document


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите логин'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })
    )


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите email'
        })
    )
    phone_number = forms.CharField(
        required=False,
        max_length=15,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите номер телефона'
        })
    )
    date_of_birth = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        input_formats=['%Y-%m-%d', '%d.%m.%Y', '%d/%m/%Y']  # Добавляем форматы дат
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'phone_number', 'date_of_birth', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите логин'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Повторите пароль'
        })

        # Убираем автоматическую помощь по паролю
        self.fields['password1'].help_text = ''
        self.fields['password2'].help_text = ''

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError('Пользователь с таким email уже существует.')
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if CustomUser.objects.filter(username=username).exists():
            raise ValidationError('Пользователь с таким логином уже существует.')
        return username


class GuestRegistrationForm(forms.ModelForm):
    fullname = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите полное имя'
        })
    )
    phonenumber = forms.IntegerField(
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите номер телефона'
        })
    )
    dateofbirth = forms.DateField(
        required=True,  # Явно указываем что поле обязательно
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        input_formats=['%Y-%m-%d', '%d.%m.%Y', '%d/%m/%Y']  # Добавляем форматы дат
    )

    class Meta:
        model = Guest
        fields = ['fullname', 'phonenumber', 'dateofbirth']

    def clean_phonenumber(self):
        phonenumber = self.cleaned_data.get('phonenumber')
        if Guest.objects.filter(phonenumber=phonenumber).exists():
            raise ValidationError('Гость с таким номером телефона уже существует.')
        return phonenumber


class DocumentForm(forms.ModelForm):
    series = forms.IntegerField(
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Серия документа'
        })
    )
    number = forms.IntegerField(
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Номер документа'
        })
    )
    dateofissue = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        input_formats=['%Y-%m-%d', '%d.%m.%Y', '%d/%m/%Y']  # Добавляем форматы дат
    )
    whoissued = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Кем выдан'
        })
    )

    class Meta:
        model = Document
        fields = ['series', 'number', 'dateofissue', 'whoissued']

    def clean(self):
        cleaned_data = super().clean()
        series = cleaned_data.get('series')
        number = cleaned_data.get('number')

        if series and number:
            if Document.objects.filter(series=series, number=number).exists():
                raise ValidationError('Документ с такой серией и номером уже существует.')

        return cleaned_data