from django.shortcuts import render, redirect
from .models import RouteItem
from .forms import RouteForm
from .utils import location_to_coords, routing
from django.conf import settings


# Create your views here.
def home(request): 
    return render(request, "home.html")

def routeItem(request):
    items = RouteItem.objects.all()
    return render(request, "routeItem.html", {"routeItem": items})

# Save the start & end destinations
def route(response):

    if response.method == "POST":
        form = RouteForm(response.POST)
        if form.is_valid():

            start_location = form.cleaned_data['start']  # Get start location from form
            end_location = form.cleaned_data['end']  # Get end location from form
            
            # Convert locations to coordinates
            start_coords = location_to_coords(start_location)
            end_coords = location_to_coords(end_location)

            print("Finished getting Coords for endpoints")

            if start_coords and end_coords:
                # Fetch routing information
                routing(start_coords, end_coords)
                
                # Redirect to main mapping page
                form.save()
                return redirect("routeItem")
            else:
                return render(request, "error.html", {"message": "Error processing locations."})

    else:
        form = RouteForm()

    context = {
        'google_key': settings.GOOGLE_KEY
    }
    return render(response, "main/route.html", {"form": form, **context})


