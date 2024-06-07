from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"), # when we go to "" calls the views function "home"
    path("todos/", views.todos, name="Todos"),
    path("route/", views.route, name="route")
]
