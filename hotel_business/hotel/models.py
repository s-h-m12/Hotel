from django.db import models
from django.db.models import ForeignKey


class Document(models.Model):
    series = models.IntegerField()
    number = models.IntegerField()
    dateofissue = models.DateField()
    whoissued = models.CharField()

class Category(models.Model):
    name = models.CharField()
    price = models.DecimalField(max_digits = 9, decimal_places = 2)
    description = models.TextField()

class Item(models.Model):
    name = models.CharField()

class Number(models.Model):
    floor = models.IntegerField()
    roomcount = models.IntegerField()
    bedcount = models.IntegerField()
    categoryid = models.ForeignKey(Category, on_delete = models.CASCADE)

class Equipment(models.Model):
    categoryid = models.ForeignKey(Category, on_delete = models.CASCADE, primary_key = True)
    itemid = models.ForeignKey(Item, on_delete = models.CASCADE)

    class Meta:
        unique_together = (('categoryid', 'itemid'),)

class Guest(models.Model):
    fullname = models.CharField()
    phonenumber = models.IntegerField()
    dateofbirth = models.DateField()
    documentid = models.ForeignKey(Document, on_delete = models.CASCADE)
    discount = models.DecimalField(max_digits = 2, decimal_places = 2)

class Service(models.Model):
    name = models.CharField()
    price = models.DecimalField(max_digits = 9, decimal_places = 2)
    description = models.TextField()

class Reservation(models.Model):
    clientid = models.ForeignKey(Guest, on_delete = models.CASCADE)
    numberid = models.ForeignKey(Number, on_delete = models.CASCADE)
    arrivaldate = models.DateField()
    departuredate = models.DateField()
    price = models.DecimalField(max_digits = 9, decimal_places = 2)
    actuallypaid = models.DecimalField(max_digits = 9, decimal_places = 2)

class ServiceProvision(models.Model):
    reservationid = models.ForeignKey(Reservation, on_delete = models.CASCADE)
    serviceid = models.ForeignKey(Service, on_delete = models.CASCADE)
    quantity = models.IntegerField()
    dateofserviceprovision = models.DateField()


