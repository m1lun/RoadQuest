from amadeus import ResponseError, Client 

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
    