from django.shortcuts import render, redirect
from .models import RouteItem, POI
from .forms import RouteForm
from .utils import location_to_coords, routing, get_restaurants, get_attractions, get_hotels
from django.conf import settings

COORD_LIMIT = 3
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
                # waypoints is array of [longitude][latitude]
                waypoints = waypoints = routing(start_coords, end_coords)     
                list_length = len(waypoints)

                pois = []

                # Hotels    
                if list_length >= 3:
                    first = 0
                    middle = list_length // 2
                    last = list_length - 1
                    selected = [first, middle, last]
                
                for i in selected:
                    waypoint = waypoints[i]
                    print(waypoint)
                    latitude = waypoint[1]
                    longitude = waypoint[0]
                    get_hotels(latitude, longitude, radius=5)
                
                # Restaurants and Attractions
                for index, waypoint in enumerate(waypoints):
                    # only select COORD_LIMIT amount of coordinates
                    if index % max(1, len(waypoints) // COORD_LIMIT) == 0:
                        print(waypoint)

                        list = get_restaurants(waypoint)

                        for poi in list:
                            pois.append(poi)

                        attractions = get_attractions(waypoint[1], waypoint[0])
                        if attractions:
                            print("attractions here:", attractions)

                to_db(pois)

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

def to_db(pois):
    for poi in pois:
        POI.objects.update_or_create(
            name=poi['name'],
            defaults={
                'type': poi['type'],
                'address': poi['address'],
                'city': poi['city'],
                'state': poi['state'],
                'postal_code': poi['postal_code'],
                'country': poi['country'],
                'latitude': poi['latitude'],
                'longitude': poi['longitude'],
                'phone_number': poi['phone_number'],
                'website': poi['website'],
                'rating': poi['rating'],
                'review_count': poi['review_count'],
                'price_level': poi['price_level'],
                'description': poi['description'],
                'amenities': poi['amenities'],
            }
        )