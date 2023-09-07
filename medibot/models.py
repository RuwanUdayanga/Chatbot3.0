from django.db import models

# Create your models here.
class Doctor(models.Model):
    doctor_id = models.CharField(max_length=10, primary_key=True)
    doctor_name = models.CharField(max_length=100)
    speciality = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.doctor_id} : {self.doctor_name} - {self.speciality}"

class Doctor_availability(models.Model):
    id = models.AutoField(primary_key=True)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    day = models.DateField()
    available = models.BooleanField()

    def __str__(self):
        availability_status = "Available" if self.available else "Not Available"
        return f"{self.doctor.doctor_id} : {self.doctor.doctor_name} - {self.doctor.speciality} - {self.day} ({availability_status})"

class Patient(models.Model):
    userID = models.CharField(primary_key=True,max_length=20, unique=True)
    username = models.CharField(max_length=50)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=15)
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.userID} : {self.first_name} {self.last_name}"

class Booking(models.Model):
    appointment_ID = models.AutoField(primary_key=True)
    patient = models.ForeignKey(Patient,on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    day = models.DateField()
    book = models.BooleanField()

    def __str__(self):
        booking_status = "Booked" if self.book else "Not Booked"
        return f"Appointment ID: {self.appointment_ID} - Patient: {self.patient.first_name} {self.patient.last_name} - Doctor: {self.doctor.doctor_name} - Date: {self.day} - Status: {booking_status}"