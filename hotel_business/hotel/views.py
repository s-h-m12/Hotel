from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Service, CustomUser, Guest, Document
from .forms import LoginForm, UserRegistrationForm, GuestRegistrationForm, DocumentForm
import logging

logger = logging.getLogger(__name__)


def register_view(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        guest_form = GuestRegistrationForm(request.POST)
        document_form = DocumentForm(request.POST)

        # Логируем сырые данные POST для отладки
        logger.debug(f"POST data: {request.POST}")

        # Логируем данные форм для отладки
        logger.debug(f"User form valid: {user_form.is_valid()}")
        logger.debug(f"Guest form valid: {guest_form.is_valid()}")
        logger.debug(f"Document form valid: {document_form.is_valid()}")

        if user_form.is_valid():
            logger.debug("User form is valid")
            logger.debug(f"User cleaned data: {user_form.cleaned_data}")
        else:
            logger.debug(f"User form errors: {user_form.errors}")

        if guest_form.is_valid():
            logger.debug("Guest form is valid")
            logger.debug(f"Guest cleaned data: {guest_form.cleaned_data}")
        else:
            logger.debug(f"Guest form errors: {guest_form.errors}")
            logger.debug(f"Guest form data: {guest_form.data}")

        if document_form.is_valid():
            logger.debug("Document form is valid")
            logger.debug(f"Document cleaned data: {document_form.cleaned_data}")
        else:
            logger.debug(f"Document form errors: {document_form.errors}")

        if user_form.is_valid() and guest_form.is_valid() and document_form.is_valid():
            try:
                # Сохраняем документ
                document = document_form.save()
                logger.debug(f"Document saved: {document}")

                # Сохраняем пользователя с ролью клиента
                user = user_form.save(commit=False)
                user.role = 'client'  # При регистрации назначаем роль клиента
                user.save()
                logger.debug(f"User saved: {user.username}")

                # Сохраняем гостя
                guest = guest_form.save(commit=False)
                guest.user = user
                guest.documentid = document
                guest.discount = 0.00  # Начальная скидка 0%
                guest.save()
                logger.debug(f"Guest saved: {guest.fullname}")

                # Автоматически авторизуем пользователя
                login(request, user)
                messages.success(request, f'Регистрация прошла успешно! Добро пожаловать, {user.username}!')
                return redirect('client_dashboard')

            except Exception as e:
                logger.error(f"Error during registration: {str(e)}")
                messages.error(request, f'Произошла ошибка при регистрации: {str(e)}')
        else:
            # Подробное сообщение об ошибках
            error_messages = []
            if not user_form.is_valid():
                error_messages.append("Ошибки в данных пользователя:")
                for field, errors in user_form.errors.items():
                    error_messages.append(f"- {field}: {', '.join(errors)}")
            if not guest_form.is_valid():
                error_messages.append("Ошибки в данных гостя:")
                for field, errors in guest_form.errors.items():
                    error_messages.append(f"- {field}: {', '.join(errors)}")
            if not document_form.is_valid():
                error_messages.append("Ошибки в данных документа:")
                for field, errors in document_form.errors.items():
                    error_messages.append(f"- {field}: {', '.join(errors)}")

            messages.error(request, '\n'.join(error_messages))

    else:
        user_form = UserRegistrationForm()
        guest_form = GuestRegistrationForm()
        document_form = DocumentForm()

    return render(request, 'auth/register.html', {
        'user_form': user_form,
        'guest_form': guest_form,
        'document_form': document_form
    })


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Добро пожаловать, {user.username}!')

                # Редирект в зависимости от роли
                if user.role == 'admin':
                    return redirect('admin_dashboard')
                elif user.role == 'manager':
                    return redirect('manager_dashboard')
                elif user.role == 'client':
                    return redirect('client_dashboard')
                else:
                    return redirect('services_list')
            else:
                messages.error(request, 'Неверные учетные данные.')
        else:
            messages.error(request, 'Ошибка в форме.')
    else:
        form = LoginForm()

    return render(request, 'auth/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'Вы вышли из системы.')
    return redirect('services_list')


def services_list(request):
    """Список услуг - доступен всем, включая неавторизованных пользователей"""
    services = Service.objects.filter(is_active=True)
    return render(request, 'services/list.html', {
        'services': services,
        'user': request.user
    })


# Декораторы для проверки прав доступа
def admin_required(function=None):
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated and u.role == 'admin',
        login_url='/login/'
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


def manager_required(function=None):
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated and u.role in ['admin', 'manager'],
        login_url='/login/'
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


def client_required(function=None):
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated and u.role in ['admin', 'manager', 'client'],
        login_url='/login/'
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


@admin_required
def admin_dashboard(request):
    return render(request, 'dashboard/admin.html')


@manager_required
def manager_dashboard(request):
    return render(request, 'dashboard/manager.html')


@client_required
def client_dashboard(request):
    return render(request, 'dashboard/client.html')