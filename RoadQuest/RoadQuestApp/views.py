from django.shortcuts import render, redirect
from django.urls import reverse
from .models import RouteItem, POI
from .forms import RouteForm
from .utils import location_to_coords, routing, get_restaurants, get_hotels
from django.conf import settings
import folium
import pandas as pd

COORD_LIMIT = 3

def home(request):
    return render(request, "home.html")

def route(response):
    if response.method == "POST":
        form = RouteForm(response.POST)
        if form.is_valid():
            # Get start & end location from form
            start_location = form.cleaned_data['start']
            end_location = form.cleaned_data['end']
            
            instance = form.save(commit=False)

            # Convert locations to coordinates
            start_coords = location_to_coords(start_location)
            end_coords = location_to_coords(end_location)

            instance.start_lat = start_coords[0]
            instance.start_lng = start_coords[1]
            instance.end_lat = end_coords[0]
            instance.end_lng = end_coords[1]
            instance.save()

            print("Finished getting Coords for endpoints")

            if start_coords and end_coords:
                # Fetch routing information
                waypoints = routing(start_coords, end_coords)
                pois = []
                
                for index, waypoint in enumerate(waypoints):
                    if index % max(1, len(waypoints) // COORD_LIMIT) == 0:
                        print(waypoint)

                        restaurants = get_restaurants(waypoint)
                        for poi in restaurants:
                            pois.append(poi)

                        hotels = get_hotels(waypoint)
                        for poi in hotels:
                            pois2.append(poi)

                to_db(pois)

                # Redirect to main mapping page
                url = reverse('mapping', kwargs={'start1': start_location, 'end1': end_location})
                return redirect(url)
      
            return render(request, "error.html", {"message": "Error processing locations."})

    else:
        form = RouteForm()

    context = {
        'google_key': settings.GOOGLE_KEY
    }
    return render(response, "main/route.html", {"form": form, **context})

def mapping(request, start1, end1):
    location = RouteItem.objects.filter(start=start1, end=end1).first()

    if not location:
        return render(request, "error.html", {"message": "Route not found."})

    # logic for map center location
    start_coord, end_coord = location.get_start_coords(), location.get_end_coords() 
    start_center = (start_coord[0] + end_coord[0]) / 2
    end_center = (start_coord[1] + end_coord[1]) / 2
    
    waypoints = routing(start_coord, end_coord)
    
    pois = POI.objects.all()

    # Example: Set initial map center and zoom
    map_center = [start_center, end_center]
    zoom_level = 8

    context = {
        'pois': pois,
        'map_center': map_center,
        'zoom_level': zoom_level,
    }
    return render(request, 'mapping.html', context)

def to_db(pois):
    for poi in pois:
        POI.objects.update_or_create(
            name=poi['name'],
            defaults={
                'type': poi['type'],
                'address': poi['address'],
                'latitude': poi['latitude'],
                'longitude': poi['longitude'],
                'rating': poi['rating'],
                'review_count': poi['review_count'],
                'price_level': poi['price_level'],
            }
        )