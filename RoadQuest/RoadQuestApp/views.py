from django.shortcuts import render, redirect
from django.urls import reverse
from .models import RouteItem, POI
from .forms import RouteForm
from .utils import location_to_coords, routing, get_restaurants, get_attractions
from django.conf import settings
import folium
import pandas as pd
COORD_LIMIT = 3

def home(request):
    return render(request, "home.html")

# Save the start & end destinations
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
                # Waypoints is an array of [longitude][latitude]
                waypoints = waypoints = routing(start_coords, end_coords)    
                pois = []
                pois2 = []
                
                # list_length = len(waypoints)
                # Hotels    
                # if list_length >= 3:
                #     first = 0
                #     middle = list_length // 2
                #     last = list_length - 1
                #     selected = [first, middle, last]
                
                # for i in selected:
                #     waypoint = waypoints[i]
                #     print(waypoint)
                #     latitude = waypoint[1]
                #     longitude = waypoint[0]
                #     hotels = get_hotels(latitude, longitude, radius=5)
                    # for poi in hotels:
                    #     pois.append(poi)
                
                # Restaurants & Attractions
                for index, waypoint in enumerate(waypoints):
                    # Only select COORD_LIMIT amount of coordinates
                    if index % max(1, len(waypoints) // COORD_LIMIT) == 0:
                        print(waypoint)

                        list = get_restaurants(waypoint)

                        for poi in list:
                            pois.append(poi)
                
                        attractions = get_attractions(waypoint[1], waypoint[0])
                        
                        for poi in attractions:
                            pois2.append(poi)

                to_db(pois)
                to_db(pois2)

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

    start_coord, end_coord = location.get_start_coords(), location.get_end_coords() 
    
    start_center = (start_coord[0] + end_coord[0]) / 2
    end_center = (start_coord[1] + end_coord[1]) / 2
    
    waypoints = routing(start_coord, end_coord)
    
    coords = []
    for item in POI.objects.all():
        coords.append(item.get_coords())

    
    data = pd.DataFrame({
        'lat': [coords[i][0] for i in range(len(coords))],
        'lon': [coords[i][1] for i in range(len(coords))]
    })
    waypoint = pd.DataFrame({
        'lat': [coord[1] for coord in waypoints],
        'lon': [coord[0] for coord in waypoints]
    })

    m = folium.Map(location=[start_center, end_center], zoom_start=8)
    
    for _, row in waypoint.iterrows():
        folium.Marker([row['lat'], row['lon']],icon=folium.Icon(color='red')).add_to(m)
        

    for _, row in data.iterrows():
        folium.Marker([row['lat'], row['lon']],icon=folium.Icon(color='blue')).add_to(m)

    context = {'map': m._repr_html_()}

    return render(request, "mapping.html", context)

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