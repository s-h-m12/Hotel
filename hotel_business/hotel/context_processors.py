# context_processors.py
from .models import Guest


def guest_profile(request):
    """Добавляет профиль гостя в контекст всех шаблонов"""
    context = {}

    if request.user.is_authenticated:
        try:
            context['guest'] = Guest.objects.get(user=request.user)
        except Guest.DoesNotExist:
            context['guest'] = None

    return context