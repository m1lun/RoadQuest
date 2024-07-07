import requests
from django.conf import settings

SEARCH_RADIUS = 10000

# convert location to [latitude, longitude]
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
            # extract latitude and longitude
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

    # parameters
    params = {
        'access_token': settings.MAPBOX_KEY, 
        'geometries': 'geojson',  
        'annotations': 'distance',
        'overview': 'full'
          
    }

    # send the GET request to Mapbox API
    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        # parse the JSON response
        data = response.json()

        if 'routes' in data and data['routes']:
            # extract the first route
            route = data['routes'][0]

            # extract waypoints from the route
            waypoints = route['geometry']['coordinates']

            distances = []

            for leg in route.get('legs', []):
                if 'annotation' in leg and 'distance' in leg['annotation']:
                    distances.extend(leg['annotation']['distance'])

            # Print distances between each pair of coordinates
            for i in range(len(distances)):
                print(f"Distance from point {i} to point {i+1}: {distances[i]} meters")

            refined_waypoints = [waypoints[0]]
            refined_distances = [0.0]
            current_distance = 0.0
            last_added_index = 0

            for i in range(1, len(waypoints)):
                segment_distance = distances[i - 1]
                current_distance += segment_distance

                # refines waypoints so they are decently spaced out
                if current_distance >= SEARCH_RADIUS * 2.0:
                    refined_waypoints.append(waypoints[i])
                    refined_distances.append(current_distance)
                    current_distance = 0.0
                    last_added_index = i

            if last_added_index != len(waypoints) - 1:
                refined_waypoints.append(waypoints[-1])
                refined_distances.append(sum(distances[last_added_index:]))

            return refined_waypoints

        else:
            print("No routes found.")
    else:
        data = response.json()
        print("API Message:", data['message'])
        print("Error:", response.status_code)

# def attraction_details(xid):
#     url = f"https://api.opentripmap.com/0.1/en/places/xid/{xid}"

#     params = {
#         'apikey': settings.OPENTRIPMAP_KEY
#     }
    
#     response = requests.get(url, params=params)
#     if response.status_code == 200:
#         return response.json()
#     else:
#         print("Error:", response.status_code)    
    
# def get_attractions(lat, long):
#     url = "https://api.opentripmap.com/0.1/en/places/radius"
    
#     if lat is None or long is None:
#         print("Invalid latitude or longitude provided.")

#     params = {
#         'apikey': settings.OPENTRIPMAP_KEY,
#         'radius': 4000,
#         'lat': lat, 
#         'lon': long,
#         'rate': 3,
#         'format': 'JSON'
#     }

#     pois = []
#     kinds = ['natural', 'cultural', 'accomodations']
#     for kind in kinds:
#         params['kinds'] = kind
#         response = requests.get(url, params=params)
#         if response.status_code == 200:
#             data = response.json()
#             for attraction in data:
#                 xid = attraction.get('xid')
#                 details = attraction_details(xid)
#                 if details:
#                     poi = {
#                         'name': attraction.get('name'),
#                         'type': ', '.join(attraction.get('kinds', '').split(',')),
#                         'address': f"{details.get('address', {}).get('house_number', '')} {details.get('address', {}).get('road', '') or details.get('address', {}).get('footway', '')}",
#                         'city': details.get('address', {}).get('city', None),
#                         'state': details.get('address', {}).get('state', None),
#                         'postal_code': details.get('address', {}).get('postcode', None),
#                         'country': details.get('address', {}).get('country', None),
#                         'latitude': attraction['point']['lat'],
#                         'longitude': attraction['point']['lon'],
#                         'phone_number': details.get('phone', None),
#                         'website': details.get('url', None),
#                         'rating': None, 
#                         'review_count': None,  
#                         'price_level': None, 
#                         'description': None,
#                         'amenities': None,  
#                     }
#                     pois.append(poi)
#         else:
#             print(f"Error fetching {kind} attractions: Status code {response.status_code}")
    # return pois

def get_pois(coordinate):
    api_key = settings.GOOGLE_KEY
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?"

    params = {
        "location": f"{coordinate[1]},{coordinate[0]}" ,
        "radius": SEARCH_RADIUS,
        "key": api_key
    }
    
    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        pois = []
        for google_poi in data.get("results", []):
            poi = {
                "name": google_poi.get("name"),
                "address": google_poi.get("vicinity"),
                "latitude": google_poi["geometry"]["location"]["lat"],
                "longitude": google_poi["geometry"]["location"]["lng"],
                "price_level": google_poi.get("price_level"),
                "rating": google_poi.get("rating"),
                "review_count": google_poi.get("user_ratings_total"),
                "type": ', '.join([t.replace('_', ' ').title() for t in google_poi.get("types", [])]),
            }
            pois.append(poi)
        # print(pois)

    else:
        print("Error:", response.status_code)

    return pois

# def get_hotels(coordinate):
#     api_key = settings.GOOGLE_KEY
#     url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?"

#     params = {
#         "location": f"{coordinate[1]},{coordinate[0]}" ,
#         "radius": 10000,
#         "type": "lodging",
#         "key": api_key
#     }
    
#     response = requests.get(url, params=params)

#     if response.status_code == 200:
#         data = response.json()
#         pois = []
#         for hotel in data.get("results", []):
#             poi = {
#                 "name": hotel.get("name"),
#                 "address": hotel.get("vicinity"),
#                 "latitude": hotel["geometry"]["location"]["lat"],
#                 "longitude": hotel["geometry"]["location"]["lng"],
#                 "price_level": hotel.get("price_level"),
#                 "rating": hotel.get("rating"),
#                 "review_count": hotel.get("user_ratings_total"),
#                 "type": "lodging"
#             }
#             pois.append(poi)
#         print(pois)

#     else:
#         print("Error:", response.status_code)

#     return pois

# amadeus = Client(
#         client_id='5vFjQOyy1Dmb5frlsK8PcGQOLgjMuLyZ',
#         client_secret='u5D2xe5MoY1Vyi0j'
# )

# def get_hotels(latitude, longitude, radius):
#     try:
#         response = amadeus.reference_data.locations.hotels.by_geocode.get(
#             latitude = latitude,
#             longitude = longitude,
#             radius = radius
#         )
#         return response.data[0]
#     except ResponseError as error:
#         raise error

# def get_restaurants(coordinate):

#     url = "https://api.yelp.com/v3/businesses/search"

#     headers = {
#         "accept": "application/json",
#         "Authorization": f"Bearer {settings.YELP_KEY}"
#     }

#     params = {
#         "latitude": f"{coordinate[1]}",
#         "longitude": f"{coordinate[0]}",
#         "radius": f"4000",
#         "limit": 1,
#         "sort_by": "best_match"
#     }

#     response = requests.get(url, headers=headers, params=params)

#     data = response.json()

#     pois = []
#     for business in data.get('businesses', []):
#         poi = {
#             'name': business.get('name'),
#             'type': ', '.join(business.get('categories', [{'title': ''}])[0]['title'].lower().split()), 
#             'address': ' '.join(business['location']['display_address']),
#             'city': business['location']['city'],
#             'state': business['location']['state'],
#             'postal_code': business['location']['zip_code'],
#             'country': business['location']['country'],
#             'latitude': business['coordinates']['latitude'],
#             'longitude': business['coordinates']['longitude'],
#             'phone_number': business.get('display_phone'),
#             'website': business.get('url'),
#             'rating': business.get('rating'),
#             'review_count': business.get('review_count'),
#             'price_level': len(business.get('price', '')) if business.get('price') else None,
#             'description': business.get('snippet_text', ''),
#             'amenities': ', '.join([feature for feature in business.get('features', [])]),
#         }
#         pois.append(poi)

#     return pois