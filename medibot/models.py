from django.db import models

# Create your models here.
class Doctor(models.Model):
    doctor_id = models.CharField(max_length=10, primary_key=True)
    doctor_name = models.CharField(max_length=100)
    speciality = models.CharField(max_length=50)

class Doctor_availability(models.Model):
    id = models.AutoField(primary_key=True)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    day = models.DateField()
    available = models.BooleanField()

class Bookings(models.Model):
    id = models.AutoField(primary_key=True)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    day = models.DateField()
    book = models.BooleanField()