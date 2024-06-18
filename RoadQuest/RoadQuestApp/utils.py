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
    
    params_natural = {
        'apikey': settings.OPENTRIPMAP_KEY,
        'radius': 5000,
        'lat': lat, 
        'lon': long,
        'rate': 3,
        'kinds': 'natural',
        'format': 'JSON'
        
    }
    
    params_cultural = {
        'apikey': settings.OPENTRIPMAP_KEY,
        'radius': 5000,
        'lat': lat, 
        'lon': long,
        'rate': 3,
        'kinds': 'cultural',
        'format': 'JSON'
        
    }
    
    params_historic = {
        'apikey': settings.OPENTRIPMAP_KEY,
        'radius': 5000,
        'lat': lat, 
        'lon': long,
        'rate': 3,
        'kinds': 'historic',
        'format': 'JSON'
        
    }
    
    params_historic_architecture = {
        'apikey': settings.OPENTRIPMAP_KEY,
        'radius': 5000,
        'lat': lat, 
        'lon': long,
        'rate': 3,
        'kinds': 'historic_architecture',
        'format': 'JSON'
        
    }
    
    params_accomodations = {
        'apikey': settings.OPENTRIPMAP_KEY,
        'radius': 5000,
        'lat': lat, 
        'lon': long,
        'rate': 3,
        'kinds': 'accomodations',
        'format': 'JSON'
        
    }
    
    pois = []

    # Fetch natural attractions
    response_natural = requests.get(url, params=params_natural)
    pois.extend(process_attractions_response(response_natural))

    # Fetch cultural attractions
    response_cultural = requests.get(url, params=params_cultural)
    pois.extend(process_attractions_response(response_cultural))

    # Fetch historic attractions
    response_historic = requests.get(url, params=params_historic)
    pois.extend(process_attractions_response(response_historic))

    response_historic_architecture = requests.get(url, params=params_historic_architecture)
    pois.extend(process_attractions_response(response_historic_architecture))
    
    response_accomodations = requests.get(url, params=params_accomodations)
    pois.extend(process_attractions_response(response_accomodations))
    
    return pois 

    
    
def process_attractions_response(response):

    # response = requests.get(url, params = params)
    
    if response.status_code == 200:
        data = response.json()
        pois = []
        for attractions in data:
            poi = {
                'name': attractions.get('name'),
                'type': ', '.join(attractions.get('kinds', '').split(',')),
                'address': None,  # Address not provided in the sample JSON
                'city': None,  # City not provided in the sample JSON
                'state': None,  # State not provided in the sample JSON
                'postal_code': None,  # Postal code not provided in the sample JSON
                'country': None,  # Country not provided in the sample JSON
                'latitude': attractions['point']['lat'],
                'longitude': attractions['point']['lon'],
                'phone_number': None,  # Phone number not provided in the sample JSON
                'website': None,  # Website not provided in the sample JSON
                'rating': None,  # Rating not provided in the sample JSON
                'review_count': None,  # Review count not provided in the sample JSON
                'price_level': None,  # Price level not provided in the sample JSON
                'description': None,  # Description not provided in the sample JSON
                'amenities': None,  # Amenities not provided in the sample JSON
            }
            pois.append(poi)
        print(response.text)
        return pois

    else: 
        print(f"Error fetching attractions: Status code {response.status_code}")



    
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
        return response.data[0]
    except ResponseError as error:
        raise error
    
