from django.db import models

# Create your models here.
class Doctor(models.Model):
    doctor_id = models.CharField(max_length=10, primary_key=True)
    doctor_name = models.CharField(max_length=100)
    id = None

class Doctor_availability(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    day = models.DateField()
    available = models.BooleanField()
