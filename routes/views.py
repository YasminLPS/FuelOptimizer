import os
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import RouteResponseSerializer
from .utils import get_route_data, calculate_fuel_stops, load_fuel_prices
from django.conf import settings
class RouteAPIView(APIView):
    def post(self, request):
        start_coords = request.data.get("start_location")
        finish_coords = request.data.get("finish_location")
        
        if not start_coords or not finish_coords:
            return Response({"error": "Start and finish locations are required!"}, status=400)
    
        file_path = os.path.join(settings.BASE_DIR, 'data/fuel-prices-for-be-assessment.csv')
        
        if not os.path.exists(file_path):
            return Response({"error": "Fuel prices file not found!"}, status=400)
        
        fuel_stations = load_fuel_prices(file_path)
        
        try:
            route_data = get_route_data(start_coords, finish_coords)
        except Exception as e:
            return Response({"error": f"Route calculation failed: {str(e)}"}, status=400)
        
        if not route_data:
            return Response({"error": "Unable to calculate route"}, status=400)
        
        fuel_stops, total_cost = calculate_fuel_stops(route_data, fuel_stations)

        route_map_url = self.get_route_map_url(route_data)

        response_data = {
            "route_map": route_map_url,
            "fuel_stops": fuel_stops,
            "total_cost": total_cost
        }

        serializer = RouteResponseSerializer(data=response_data)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data)
    
    def get_route_map_url(self, route_data):
        if not route_data or not route_data.get('features'):
            raise ValueError("Invalid route data")
        
        coordinates = route_data['features'][0]['geometry']['coordinates']
        
        start_coords = coordinates[0][::-1]
        end_coords = coordinates[-1][::-1] 

        route_map_url = f"https://maps.openrouteservice.org/directions/{start_coords[0]},{start_coords[1]}:{end_coords[0]},{end_coords[1]}"
        return route_map_url
