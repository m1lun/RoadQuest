from django.db import models

# Create your models here.
class RouteItem(models.Model):
    start = models.CharField(max_length=200)
    end = models.CharField(max_length=200)

    def __str__(self):
        return f"Route from {self.start} to {self.end}"