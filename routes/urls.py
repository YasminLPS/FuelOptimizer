from django.urls import path
from .views import RouteAPIView

urlpatterns = [
    path('api/route/', RouteAPIView.as_view(), name='route-api')
]