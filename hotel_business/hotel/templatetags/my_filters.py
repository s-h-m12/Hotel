from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter(name='format_price_with_discount')
def format_price_with_discount(service, guest):
    """
    Форматирует цену услуги с учетом скидки гостя.
    Если у клиента есть скидка, то старую цену услуги зачеркнуть, рядом
    написать новую цену с учетом скидки и подсветить ее красным цветом.
    """
    if not service:
        return mark_safe('<span>0.00 руб.</span>')

    try:
        service_price = float(service.price)
    except (AttributeError, TypeError, ValueError):
        return mark_safe(f'<span>0.00 руб.</span>')

    # Если гость не передан или нет скидки
    if not guest or not hasattr(guest, 'discount'):
        return mark_safe(f'<span>{service_price:.2f} руб.</span>')

    try:
        guest_discount = float(guest.discount)
    except (TypeError, ValueError):
        guest_discount = 0

    if guest_discount > 0:
        # Рассчитываем цену со скидкой
        discounted_price = service_price * (1 - guest_discount)

        # Формируем HTML с зачеркнутой старой ценой и красной новой
        html = f'''
        <span class="price-old">{service_price:.2f} руб.</span>
        <span class="price-new">{discounted_price:.2f} руб.</span>
        '''
        return mark_safe(html)
    else:
        # Если скидки нет
        return mark_safe(f'<span>{service_price:.2f} руб.</span>')


@register.filter(name='has_high_discount')
def has_high_discount(guest):
    """Проверяет, есть ли у гостя скидка более 10%."""
    if not guest or not hasattr(guest, 'discount'):
        return False

    try:
        guest_discount = float(guest.discount)
        return guest_discount > 0.10  # Более 10%
    except (TypeError, ValueError):
        return False