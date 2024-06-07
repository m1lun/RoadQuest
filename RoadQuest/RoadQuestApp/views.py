from django.shortcuts import render, HttpResponse
from .models import TodoItem
from .forms import CreateNewRoute

# Create your views here.
def home(request): 
    return render(request, "home.html")

def todos(request):
    items = TodoItem.objects.all()
    return render(request, "todos.html", {"todos": items})

def route(response):
    form = CreateNewRoute()
    return render(response, "main/route.html", {"form":form} )