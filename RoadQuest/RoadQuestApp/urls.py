from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home") # when we go to "" calls the views function "home"
]