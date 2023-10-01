from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def index(request):
    return HttpResponse("Hello, Welcome to medibot")

def home(request):
    return render(request, 'index.html')