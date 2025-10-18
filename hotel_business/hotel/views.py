from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Service, CustomUser
from .forms import LoginForm


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


# Пример защищенных представлений
@admin_required
def admin_dashboard(request):
    return render(request, 'dashboard/admin.html')


@manager_required
def manager_dashboard(request):
    return render(request, 'dashboard/manager.html')


@client_required
def client_dashboard(request):
    return render(request, 'dashboard/client.html')