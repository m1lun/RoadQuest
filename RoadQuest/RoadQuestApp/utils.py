import requests
from django.conf import settings

# converts location to [latitude, longitude]
# using OpenStreetMap Nominatim API
def location_to_coords(location_name):

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
    base_url = f"https://api.mapbox.com/directions/v5/mapbox/driving/{start_coords[1]},{start_coords[0]};{end_coords[1]}, {end_coords[0]}"

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