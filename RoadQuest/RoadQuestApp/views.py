from django.shortcuts import render, redirect
from django.urls import reverse
from .models import RouteItem, POI
from .forms import RouteForm
from .utils import location_to_coords, routing, get_pois
from django.conf import settings
from django.db.models import Q
import folium
import pandas as pd
import uuid

COORD_LIMIT = 3

def home(request):
    return render(request, "home.html")

def get_or_create_session_user_id(request):
    if 'user_id' not in request.session:
        request.session['user_id'] = str(uuid.uuid4())
    return request.session['user_id']

# Save the start & end destinations
def route(request):
    
    user_id = get_or_create_session_user_id(request)
    delete_pois(user_id)
    if request.method == "POST":
        form = RouteForm(request.POST)
        if form.is_valid():
            # Get start & end location from form
            start_location = form.cleaned_data['start']
            end_location = form.cleaned_data['end']
            
            instance = form.save(commit=False)
            instance.user_id = user_id

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

                print(f"Finished getting Coords for {len(waypoints)} intermediate points")

                pois = []
                
                for index, waypoint in enumerate(waypoints):
                    # if index % max(1, len(waypoints) // COORD_LIMIT) == 0:

                    google_pois = get_pois(waypoint)
                    for poi in google_pois:
                        pois.append(poi)

                    print(f"Found POIS for waypoint: {index + 1} / {len(waypoints)}")

                print(f"Sent {len(waypoints)} Google API requests for all POIs")
                to_db(pois, user_id)

                # Redirect to main mapping page
                url = reverse('mapping', kwargs={'start1': start_location, 'end1': end_location})
                return redirect(url)
      
            return render(request, "error.html", {"message": "Error processing locations."})

    else:
        form = RouteForm()

    context = {
        'google_key': settings.GOOGLE_KEY
    }
    return render(request, "main/route.html", {"form": form, **context})

def mapping(request, start1, end1, poi_type = ""):
    
    user_id = get_or_create_session_user_id(request)
    location = RouteItem.objects.filter(user_id=user_id, start=start1, end=end1).first()
    if not location:
        return render(request, "error.html", {"message": "Route not found."})

    # logic for map center location
    start_coord, end_coord = location.get_start_coords(), location.get_end_coords() 
    start_center = (start_coord[0] + end_coord[0]) / 2
    end_center = (start_coord[1] + end_coord[1]) / 2
    poi_type = 'lodging'
    poi_rating = 4.0
    poi_keyword = 'hotel'
    pois = list(filter_pois(user_id, poi_type, poi_rating, poi_keyword))
    print(f"Found {len(pois)} hotels")
    waypoints  = routing(start_coord, end_coord)
    
    print(f"Gathered {len(pois)} out of {len(POI.objects.all())} total POIs")
        
    map_center = [start_center, end_center]
    zoom_level = 8

    

    context = {
        'pois': pois,
        'map_center': map_center,
        'zoom_level': zoom_level,
        'current_filter': poi_type,
        'start1': start1,
        'end1': end1,
        'waypoints' : waypoints
        
    }

    return render(request, 'mapping.html', context)

def delete_pois(user_id):
    RouteItem.objects.filter(user_id=user_id).delete()
    POI.objects.filter(user_id=user_id).delete()
    print(f"Deleted POIS for {user_id}")
    
def filter_pois(user_id, poi_type, poi_rating=None, poi_keyword=None):
    
    if(poi_type == ""):
        return POI.objects.filter(user_id=user_id)
    
    query = POI.objects.filter(user_id=user_id).filter(Q(type__icontains=poi_type))
    
    if poi_rating is not None:
        query = query.filter(rating__gte=poi_rating)
        
    if poi_keyword:
        query = query.filter(Q(name__icontains=poi_keyword) | Q(address__icontains=poi_keyword))

    return query
    
def to_db(pois, user_id):
    for poi in pois:
        POI.objects.update_or_create(
            user_id = user_id,
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