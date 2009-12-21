from django.db import models

class Manufacturer(models.Model):
    name = models.CharField(max_length=200)
    address = models.TextField()

class Usage(models.Model):
    description = models.CharField(max_length=200)

class CPU(models.Model):
    manufacturer = models.ForeignKey(Manufacturer)
    model = models.CharField(max_length=200)

class HardDisk(models.Model):
    manufacturer = models.ForeignKey(Manufacturer)
    model = models.CharField(max_length=200)

class DesktopPC(models.Model):
    model = models.CharField(max_length=200)
    price = models.FloatField()
    manufacturer = models.ForeignKey(Manufacturer)
    usage = models.ForeignKey(Usage)
    cpu = models.ForeignKey(CPU)
    hdd = models.ForeignKey(HardDisk)
