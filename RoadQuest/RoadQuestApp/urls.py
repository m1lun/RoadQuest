from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"), # when we go to "" calls the views function "home"
    path("routeItem/", views.routeItem, name="routeItem"),
    path("route/", views.route, name="route")
]
