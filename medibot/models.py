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

class Patient(models.Model):
    userID = models.CharField(primary_key=True,max_length=20, unique=True)
    username = models.CharField(max_length=50)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=15)
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)

class Bookings(models.Model):
    appointment_ID = models.AutoField(primary_key=True)
    patient = models.ForeignKey(Patient,on_delete=models.PROTECT)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    day = models.DateField()
    book = models.BooleanField()