from django.shortcuts import render, HttpResponse, redirect
from .models import RouteItem
from .forms import RouteForm


# Create your views here.
def home(request): 
    return render(request, "home.html")

def routeItem(request):
    items = RouteItem.objects.all()
    return render(request, "routeItem.html", {"routeItem": items})

def route(response):
    if response.method == "POST":
        form = RouteForm(response.POST)
        if form.is_valid():
            form.save()
            return redirect("routeItem")
            # need redirect to an URL
    else:
        form = RouteForm()
    return render(response, "main/route.html", {"form": form})

