from rest_framework import serializers

class RouteResponseSerializer(serializers.Serializer):
    route_map = serializers.URLField()
    fuel_stops = serializers.ListField(
        child=serializers.DictField()
    )
    total_cost = serializers.FloatField()