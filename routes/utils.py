import openrouteservice
from django.conf import settings
import csv

def get_route_data(start_coords, finish_coords):
    client = openrouteservice.Client(key=settings.OPENROUTESERVICE_API_KEY)

    start_coords_correct = [start_coords[1], start_coords[0]]  
    finish_coords_correct = [finish_coords[1], finish_coords[0]]  

    print(f"Start Coordinates: {start_coords_correct}")
    print(f"Finish Coordinates: {finish_coords_correct}")

    try:
        route = client.directions(
            coordinates=[start_coords_correct, finish_coords_correct],
            profile='driving-car',
            format='geojson'
        )
        return route
    except Exception as e:
        print(f"Error in route calculation: {str(e)}")
        return None

def load_fuel_prices(file_path):
    fuel_stations = []

    with open(file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if 'Truckstop Name' not in row or 'Retail Price' not in row or not row['Retail Price']:
                continue  
            try:
                price = float(row['Retail Price'])
            except ValueError:
                continue  
            
            fuel_stations.append({
                'name': row['Truckstop Name'],
                'address': row['Address'],
                'city': row['City'],
                'state': row['State'],
                'price_per_gallon': price
            })

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
        
        fuel_stops.append({
            "name": optimal_station['name'],
            "address": optimal_station['address'],
            "city": optimal_station['city'],
            "state": optimal_station['state'],
            "price_per_gallon": optimal_station['price_per_gallon'],
            "cost": cost
        })
        
        remaining_distance -= max_range

    return fuel_stops, total_cost