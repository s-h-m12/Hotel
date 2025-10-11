from django.db import models
from django.db.models import ForeignKey


class Document(models.Model):
    """Модель документа, удостоверяющего личность гостя (паспорт и т.д.)"""
    series = models.IntegerField()
    number = models.IntegerField()
    dateofissue = models.DateField()
    whoissued = models.CharField()

class Category(models.Model):
    """Модель категории номера (люкс, стандарт, эконом и т.д.)"""
    name = models.CharField()
    price = models.DecimalField(max_digits=9, decimal_places=2)
    description = models.TextField()

class Item(models.Model):
    """Модель предмета/оборудования в номере (телевизор, холодильник и т.д.)"""
    name = models.CharField()

class Number(models.Model):
    """Модель номера отеля"""
    floor = models.IntegerField()
    roomcount = models.IntegerField()
    bedcount = models.IntegerField()
    categoryid = models.ForeignKey(Category, on_delete=models.CASCADE)

class Equipment(models.Model):
    """Промежуточная модель для связи категорий и оборудования (многие-ко-многим)"""
    categoryid = models.ForeignKey(Category, on_delete=models.CASCADE, primary_key=True)  # Категория
    itemid = models.ForeignKey(Item, on_delete=models.CASCADE)  # Предмет оборудования

    class Meta:
        unique_together = (('categoryid', 'itemid'),)  # Композитный первичный ключ через класс Meta

class Guest(models.Model):
    """Модель гостя отеля"""
    fullname = models.CharField()
    phonenumber = models.IntegerField()
    dateofbirth = models.DateField()
    documentid = models.ForeignKey(Document, on_delete=models.CASCADE)
    discount = models.DecimalField(max_digits=2, decimal_places=2)  # Размер скидки (в долях)

class Service(models.Model):
    """Модель дополнительной услуги (завтрак, спа и т.д.)"""
    name = models.CharField()
    price = models.DecimalField(max_digits=9, decimal_places=2)
    description = models.TextField()

class Reservation(models.Model):
    """Модель бронирования номера"""
    clientid = models.ForeignKey(Guest, on_delete=models.CASCADE)
    numberid = models.ForeignKey(Number, on_delete=models.CASCADE)
    arrivaldate = models.DateField()
    departuredate = models.DateField()
    price = models.DecimalField(max_digits=9, decimal_places=2)
    actuallypaid = models.DecimalField(max_digits=9, decimal_places=2)

class ServiceProvision(models.Model):
    """Модель оказания услуги гостю (связь многие-ко-многим с дополнительными данными)"""
    reservationid = models.ForeignKey(Reservation, on_delete=models.CASCADE)
    serviceid = models.ForeignKey(Service, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    dateofserviceprovision = models.DateField()