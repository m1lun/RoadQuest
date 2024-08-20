from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"), # when we go to "" calls the views function "home"
    path('mapping/<str:start1>/<str:end1>/', views.mapping, name='mapping'),
    path('mapping/<str:start1>/<str:end1>/<str:poi_types>/<str:poi_rating>/', views.mapping, name='mapping_filtered'),
    path("route/", views.route, name="route")
]
