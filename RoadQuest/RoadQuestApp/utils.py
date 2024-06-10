import requests

# converts location to [latitude, longitude]
# using OpenStreetMap Nominatim API
def location_to_coords(location_name):

    base_url = "http://api.openweathermap.org/geo/1.0/direct"
    
    params = {
        "q": f"{location_name}",
        "limit": 1,
        "appid": "69181b403bcaff728ca2d4bfff10dc24"
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
    
    # fetch route waypoints with options for driving
    response = requests.get(f"http://router.project-osrm.org/route/v1/driving/{start_coords[1]},{start_coords[0]};{end_coords[1]},{end_coords[0]}?overview=full")

    print("attempting:" f"http://router.project-osrm.org/route/v1/driving/{start_coords[1]},{start_coords[0]};{end_coords[1]},{end_coords[0]}?overview=full")
    
    if response.status_code == 200:
        # Parse the JSON response
        data = response.json()

        if 'routes' in data and data['routes']:
            # Print each route waypoint
            for waypoint in data['waypoints']:
                latitude, longitude = waypoint['location']
                print("Latitude:", latitude)
                print("Longitude:", longitude)
        else:
            print("No routes found.")
    else:
        print("Error:", response.status_code)