from django.contrib import admin

# Register your models here.
from .models import Doctor
from .models import Patient
from .models import Bookings
from .models import Doctor_availability

admin.site.register(Doctor)
admin.site.register(Patient)
admin.site.register(Doctor_availability)
admin.site.register(Bookings)
