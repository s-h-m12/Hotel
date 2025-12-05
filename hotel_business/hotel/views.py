from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Service, CustomUser, Guest, Document, ServiceProvision
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


        if user_form.is_valid() and document_form.is_valid():
            try:
                # Сохраняем документ
                document = document_form.save()
                logger.debug(f"Document saved: {document}")

                # Сохраняем пользователя с ролью клиента
                user = user_form.save(commit=False)
                user.role = 'client'  # При регистрации назначаем роль клиента
                user.save()
                logger.debug(f"User saved: {user.username}")


                guest_data = {
                    'user': user,
                    'documentid': document,
                    'fullname': request.POST.get('fullname', ''),
                    'phonenumber': request.POST.get('phonenumber', ''),
                    'discount': 0.00,  # Начальная скидка 0%
                }

                # Берем дату рождения из пользовательской формы
                if user_form.cleaned_data.get('date_of_birth'):
                    guest_data['dateofbirth'] = user_form.cleaned_data['date_of_birth']
                else:
                    # Или из POST данных напрямую
                    guest_data['dateofbirth'] = request.POST.get('date_of_birth')

                # Создаем гостя
                guest = Guest(**guest_data)
                guest.save()
                logger.debug(f"Guest saved: {guest.fullname}, dateofbirth: {guest.dateofbirth}")

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
    services = Service.objects.all()
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


# views.py
from django.shortcuts import render
from django.db.models import Q
from django.utils import timezone
from .models import Guest, Service, Number, Category, Reservation


def manager_dashboard(request):
    """Главная страница панели менеджера"""
    context = {
        'guests_count': Guest.objects.count(),
        'services_count': Service.objects.filter(is_active=True).count(),
        'rooms_count': Number.objects.count(),
        'available_rooms_count': Number.objects.filter(is_available=True).count(),
    }
    return render(request, 'manager/manager_dashboard.html', context)


def manager_guests(request):
    guests = Guest.objects.select_related('user', 'documentid').all()

    # Поиск
    search_query = request.GET.get('q', '')
    if search_query:
        guests = guests.filter(
            Q(fullname__icontains=search_query) |
            Q(phonenumber__icontains=search_query) |
            Q(user__email__icontains=search_query) |
            Q(user__username__icontains=search_query) |
            Q(documentid__series__icontains=search_query) |
            Q(documentid__number__icontains=search_query)
        )

    # Сортировка
    sort = request.GET.get('sort', '')
    if sort == 'name_asc':
        guests = guests.order_by('fullname')
    elif sort == 'name_desc':
        guests = guests.order_by('-fullname')
    elif sort == 'discount_desc':
        guests = guests.order_by('-discount')
    elif sort == 'date_asc':
        guests = guests.order_by('dateofbirth')
    else:
        # Сортировка по умолчанию (по ID)
        guests = guests.order_by('id')

    context = {
        'guests': guests,
        'sort': sort,
    }
    return render(request, 'manager/guests.html', context)


def manager_services(request):
    """Страница услуг"""
    services = Service.objects.filter(is_active=True)
    all_services_count = Service.objects.count()

    # Поиск услуг
    query = request.GET.get('q', '')
    if query:
        services = services.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query)
        )

    context = {
        'services': services,
        'all_services_count': all_services_count,
    }
    return render(request, 'manager/services.html', context)


def manager_rooms(request):
    """Страница номеров с фильтрацией"""
    rooms = Number.objects.all()
    categories = Category.objects.all()

    # Фильтрация номеров
    bed_count = request.GET.get('bed_count')
    category_id = request.GET.get('category')

    if bed_count:
        rooms = rooms.filter(bedcount=bed_count)
    if category_id:
        rooms = rooms.filter(categoryid_id=category_id)

    # Уникальные значения количества кроватей для фильтра
    bed_counts = Number.objects.values_list('bedcount', flat=True).distinct().order_by('bedcount')

    context = {
        'rooms': rooms,
        'categories': categories,
        'bed_counts': bed_counts,
        'selected_bed_count': bed_count,
        'selected_category': category_id,
    }
    return render(request, 'manager/rooms.html', context)


def manager_assignment(request):
    """Страница назначения услуг"""
    guests = Guest.objects.all()
    services = Service.objects.filter(is_active=True)
    reservations = Reservation.objects.filter(status='active')

    # Получаем последние 5 назначений услуг
    recent_assignments = ServiceProvision.objects.select_related(
        'reservationid__clientid', 'serviceid'
    ).order_by('-dateofserviceprovision')[:5]

    if request.method == 'POST':
        try:
            # Получаем данные из формы
            guest_id = request.POST.get('guest')
            reservation_id = request.POST.get('reservation')
            service_id = request.POST.get('service')
            quantity = int(request.POST.get('quantity', 1))
            date_of_service = request.POST.get('date_of_service')

            # Проверяем существование объектов
            guest = Guest.objects.get(id=guest_id)
            reservation = Reservation.objects.get(id=reservation_id)
            service = Service.objects.get(id=service_id)

            # Создаем запись об оказании услуги
            ServiceProvision.objects.create(
                reservationid=reservation,
                serviceid=service,
                quantity=quantity,
                dateofserviceprovision=date_of_service
            )

            messages.success(request, f'Услуга "{service.name}" успешно назначена гостю {guest.fullname}')
            return redirect('manager_assignment')

        except Exception as e:
            messages.error(request, f'Ошибка при назначении услуги: {str(e)}')

    context = {
        'guests': guests,
        'services': services,
        'reservations': reservations,
        'recent_assignments': recent_assignments,
        'today': timezone.now().date(),
    }
    return render(request, 'manager/assignment.html', context)


@client_required
def client_dashboard(request):
    services = Service.objects.all()
    users = CustomUser.objects.all()
    guests = Guest.objects.all()

    return render(request, 'client/client_dashboard.html', {'services': services, 'users': users, 'guests': guests})
