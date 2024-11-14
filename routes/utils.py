import pandas as pd
import openrouteservice
from django.conf import settings

def get_route_data(start_coords, finish_coords):
    client = openrouteservice.Client(key=settings.OPENROUTESERVICE_API_KEY)
    
    route = client.directions(
        coordinates=[start_coords, finish_coords], 
        profile='driving-car', 
        format='geojson'  
    )
    
    return route

def load_fuel_prices(csv_file):
    fuel_data = pd.read_csv(csv_file)
    
    fuel_stations = fuel_data.to_dict(orient="records")
    return fuel_stations

def calculate_fuel_stops(route_data, fuel_stations, max_range=500, mpg=10):
    total_distance_m = route_data['features'][0]['properties']['segments'][0]['distance']
    total_distance_miles = total_distance_m / 1609.34 

    fuel_needed = total_distance_miles / mpg  

    fuel_stops = []
    remaining_distance = total_distance_miles
    total_cost = 0

    while remaining_distance > 0:
        optimal_station = min(fuel_stations, key=lambda x: x['price_per_gallon'])
        cost = optimal_station['price_per_gallon'] * (max_range / mpg)
        total_cost += cost
        fuel_stops.append({"location": optimal_station['location'], "cost": cost})
        
        remaining_distance -= max_range

    return fuel_stops, total_cost
