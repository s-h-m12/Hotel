from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import ForeignKey


class CustomUser(AbstractUser):
    """Расширенная модель пользователя с ролями"""
    ROLE_CHOICES = (
        ('admin', 'Администратор'),
        ('manager', 'Менеджер'),
        ('client', 'Клиент'),
        ('guest', 'Гость'),
    )

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='guest')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


class Document(models.Model):
    """Модель документа, удостоверяющего личность гостя (паспорт и т.д.)"""
    series = models.IntegerField()
    number = models.IntegerField()
    dateofissue = models.DateField()
    whoissued = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.series} {self.number}"


class Category(models.Model):
    """Модель категории номера (люкс, стандарт, эконом и т.д.)"""
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=9, decimal_places=2)
    description = models.TextField()

    def __str__(self):
        return self.name


class Item(models.Model):
    """Модель предмета/оборудования в номере (телевизор, холодильник и т.д.)"""
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Number(models.Model):
    """Модель номера отеля"""
    floor = models.IntegerField()
    roomcount = models.IntegerField()
    bedcount = models.IntegerField()
    categoryid = models.ForeignKey(Category, on_delete=models.CASCADE)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"Номер {self.id} - {self.floor} этаж"


class Equipment(models.Model):
    """Промежуточная модель для связи категорий и оборудования (многие-ко-многим)"""
    categoryid = models.ForeignKey(Category, on_delete=models.CASCADE)
    itemid = models.ForeignKey(Item, on_delete=models.CASCADE)

    class Meta:
        unique_together = (('categoryid', 'itemid'),)


class Guest(models.Model):
    """Модель гостя отеля"""
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='guest_profile')
    fullname = models.CharField(max_length=255)
    phonenumber = models.IntegerField()
    dateofbirth = models.DateField()
    documentid = models.ForeignKey(Document, on_delete=models.CASCADE)
    discount = models.DecimalField(max_digits=3, decimal_places=2)

    def __str__(self):
        return self.fullname




class Service(models.Model):
    """Модель дополнительной услуги (завтрак, спа и т.д.)"""
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=9, decimal_places=2)
    description = models.TextField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def discount_price(self, x):
        return self.price * (1 - x.discount)

class Reservation(models.Model):
    """Модель бронирования номера"""
    clientid = models.ForeignKey(Guest, on_delete=models.CASCADE)
    numberid = models.ForeignKey(Number, on_delete=models.CASCADE)
    arrivaldate = models.DateField()
    departuredate = models.DateField()
    price = models.DecimalField(max_digits=9, decimal_places=2)
    actuallypaid = models.DecimalField(max_digits=9, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='active', choices=(
        ('active', 'Активно'),
        ('completed', 'Завершено'),
        ('cancelled', 'Отменено'),
    ))

    def __str__(self):
        return f"Бронь #{self.id} - {self.clientid}"


class ServiceProvision(models.Model):
    """Модель оказания услуги гостю (связь многие-ко-многим с дополнительными данными)"""
    reservationid = models.ForeignKey(Reservation, on_delete=models.CASCADE)
    serviceid = models.ForeignKey(Service, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    dateofserviceprovision = models.DateField()

    def __str__(self):
        return f"{self.serviceid} для {self.reservationid}"