from django.db import models
import uuid

# Create your models here.
class RouteItem(models.Model):
    user_id = models.UUIDField(default=uuid.uuid4, editable=False)
    start = models.CharField(max_length=200)
    end = models.CharField(max_length=200)
    start_lat = models.FloatField(blank=True, null=True)
    start_lng = models.FloatField(blank=True, null=True)
    end_lat = models.FloatField(blank=True, null=True)
    end_lng = models.FloatField(blank=True, null=True)
    stop1 = models.CharField(max_length=200, blank=True)
    stop2 = models.CharField(max_length=200, blank=True)
    stop3 = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"Route from {self.start} ({self.start_lat}, {self.start_lng}) to {self.end} ({self.end_lat}, {self.end_lng})"
    
    def get_start_coords(self):
        return (self.start_lat, self.start_lng)
    
    def get_end_coords(self):
        return (self.end_lat, self.end_lng)
    
class POI(models.Model):
    user_id = models.UUIDField(default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=255)  # e.g., 'restaurant', 'hotel'
    address = models.CharField(max_length=255, null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    rating = models.FloatField(null=True, blank=True)
    review_count = models.IntegerField(null=True, blank=True)
    price_level = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.name
    
    def get_coords(self):
        return (self.latitude, self.longitude)
    
    def get_name(self):
        return (self.name)
    
    def get_type(self):
        return (self.type)