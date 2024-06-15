import requests
from django.conf import settings
from amadeus import ResponseError, Client 

# converts location to [latitude, longitude]
# using OpenStreetMap Nominatim API
def location_to_coords(location_name):
    #test
    base_url = "http://api.openweathermap.org/geo/1.0/direct"

    params = {
        "q": f"{location_name}",
        "limit": 1,
        "appid": settings.OWM_KEY
    }

    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        data = response.json()
        if data:
            # Extract latitude and longitude and return
            latitude = data[0]["lat"]
            longitude = data[0]["lon"]
            print(latitude)
            print(longitude)
            return latitude, longitude
        else:
            print("No results found for the location:", location_name)
            return None, None
    else:
        print("Error:", response.status_code)
        return None, None

# send api request to route given start and end coordinates
# start_coords: [latitude, longitude]
# using OSRM API
def routing(start_coords, end_coords):

    # Mapbox Directions API endpoint
    base_url = f"https://api.mapbox.com/directions/v5/mapbox/driving/{start_coords[1]},{start_coords[0]};{end_coords[1]},{end_coords[0]}"
    print(f"attempting https://api.mapbox.com/directions/v5/mapbox/driving/{start_coords[1]},{start_coords[0]};{end_coords[1]},{end_coords[0]}")

    # Parameters
    params = {
        'access_token': settings.MAPBOX_KEY, 
        'geometries': 'geojson',  
        'steps': 'true'  
    }

    # Send the GET request to Mapbox API
    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        # Parse the JSON response
        data = response.json()

        if 'routes' in data and data['routes']:
            # Extract the first route
            route = data['routes'][0]

            # Extract waypoints from the route
            waypoints = route['geometry']['coordinates']
            for waypoint in waypoints:
                longitude, latitude = waypoint
                print("Latitude:", latitude)
                print("Longitude:", longitude)

            return waypoints

        else:
            print("No routes found.")
    else:
        data = response.json()
        print("API Message:", data['message'])
        print("Error:", response.status_code)

# finds restaurants near coordinate [longitude][latitude]
def get_restaurants(coordinate):

    url = "https://api.yelp.com/v3/businesses/search"

    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {settings.YELP_KEY}"
    }

    params = {
        "latitude": f"{coordinate[1]}",
        "longitude": f"{coordinate[0]}",
        "radius": f"4000",
        "limit": 1,
        "sort_by": "best_match"

    }

    response = requests.get(url, headers=headers, params=params)

    data = response.json()

    pois = []
    for business in data.get('businesses', []):
        poi = {
            'name': business.get('name'),
            'type': ', '.join(business.get('categories', [{'title': ''}])[0]['title'].lower().split()), 
            'address': ' '.join(business['location']['display_address']),
            'city': business['location']['city'],
            'state': business['location']['state'],
            'postal_code': business['location']['zip_code'],
            'country': business['location']['country'],
            'latitude': business['coordinates']['latitude'],
            'longitude': business['coordinates']['longitude'],
            'phone_number': business.get('display_phone'),
            'website': business.get('url'),
            'rating': business.get('rating'),
            'review_count': business.get('review_count'),
            'price_level': len(business.get('price', '')) if business.get('price') else None,
            'description': business.get('snippet_text', ''),
            'amenities': ', '.join([feature for feature in business.get('features', [])]),
        }
        pois.append(poi)

    return pois

    
def get_attractions(lat, long):
    url = "https://api.opentripmap.com/0.1/en/places/radius"
    
    params = {
        'apikey': settings.OPENTRIPMAP_KEY,
        'radius': 5000,
        'lat': lat,
        'lon': long,
        'rate': 2,
        'format': 'JSON'
        
    }
    response = requests.get(url, params = params)
    
    if response.status_code == 200:
        data = response.json()
        attractions = [place['name']for place in data if 'name' in place]
        return attractions
    
    else: 
        return None
    
amadeus = Client(
        client_id='5vFjQOyy1Dmb5frlsK8PcGQOLgjMuLyZ',
        client_secret='u5D2xe5MoY1Vyi0j'
)

def get_hotels(latitude, longitude, radius):
    try:
        response = amadeus.reference_data.locations.hotels.by_geocode.get(
            latitude = latitude,
            longitude = longitude,
            radius = radius
        )
        print(response.data[0])
        return response.data
    except ResponseError as error:
        raise error
    
