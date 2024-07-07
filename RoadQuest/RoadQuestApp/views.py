from django.shortcuts import render, redirect
from django.urls import reverse
from .models import RouteItem, POI
from .forms import RouteForm
from .utils import location_to_coords, routing, get_restaurants, get_hotels
from django.conf import settings
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
                # Waypoints is an array of [longitude][latitude]
                waypoints = waypoints = routing(start_coords, end_coords)    
                pois = []
                pois2 = []
                
                # Restaurants & Attractions
                for index, waypoint in enumerate(waypoints):
                    # Only select COORD_LIMIT amount of coordinates
                    if index % max(1, len(waypoints) // COORD_LIMIT) == 0:
                        print(waypoint)

                        restaurants = get_restaurants(waypoint)
                        for poi in restaurants:
                            pois.append(poi)

                        hotels = get_hotels(waypoint)
                        for poi in hotels:
                            pois2.append(poi)

                to_db(pois, user_id)
                to_db(pois2, user_id)

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

def mapping(request, start1, end1):
    user_id = get_or_create_session_user_id(request)
    location = RouteItem.objects.filter(user_id=user_id, start=start1, end=end1).first()

    start_coord, end_coord = location.get_start_coords(), location.get_end_coords() 
    
    start_center = (start_coord[0] + end_coord[0]) / 2
    end_center = (start_coord[1] + end_coord[1]) / 2
    
    waypoints = routing(start_coord, end_coord)
    
    info = []
    for item in POI.objects.filter(user_id = user_id):
        info.append({"name": item.get_name(), "type": item.get_type(), "coords": item.get_coords()})
    
    waypoint = pd.DataFrame({
        'lat': [coord[1] for coord in waypoints],
        'lon': [coord[0] for coord in waypoints]
    })

    m = folium.Map(location=[start_center, end_center], zoom_start=8)
        
    for _, row in waypoint.iterrows():
        folium.Marker([row['lat'], row['lon']],icon=folium.Icon(color='red')).add_to(m)
        
    for item in info:
        folium.Marker(item.get("coords"), popup=item.get("name"), icon=folium.Icon(color='blue')).add_to(m)

    context = {'map': m._repr_html_()}
    
    RouteItem.objects.filter(user_id=user_id).delete()
    POI.objects.filter(user_id=user_id).delete()

    return render(request, "mapping.html", context)

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