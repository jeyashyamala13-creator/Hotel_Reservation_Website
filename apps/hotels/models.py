from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

# 1. Hotel Amenities (WiFi, AC, Pool, etc.)
class Amenity(models.Model):
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, help_text="Tailwind icon class", blank=True, null=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = 'Amenities'

# 2. Hotel Details
class Hotel(models.Model):
    name = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='hotels/')
    star_rating = models.IntegerField(default=3, validators=[MinValueValidator(1), MaxValueValidator(5)])
    
    # Core Amenities for easy backend filtering
    has_ac = models.BooleanField(default=True, verbose_name="AC Available")
    has_breakfast = models.BooleanField(default=False, verbose_name="Free Breakfast")
    has_pool = models.BooleanField(default=False, verbose_name="Swimming Pool")
    has_parking = models.BooleanField(default=True, verbose_name="Free Parking")
    
    is_popular = models.BooleanField(default=False, verbose_name="Trending/Popular Stay")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.location})"

    @property
    def starting_price(self):
        # Calculates the lowest room category price dynamically
        cheapest_room = self.categories.order_by('price_per_night').first()
        return cheapest_room.price_per_night if cheapest_room else 0

    @property
    def available_rooms_count(self):
        # Calculates actual available total rooms across categories perfectly
        total_rooms = 0
        for category in self.categories.all():
            total_rooms += category.rooms.filter(is_available=True).count()
        return total_rooms


class RoomCategory(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='categories')
    type_name = models.CharField(max_length=100) # e.g., Deluxe Suite, Standard AC
    price_per_night = models.DecimalField(max_digits=12, decimal_places=2)
    capacity = models.IntegerField(default=2)
    image = models.ImageField(upload_to='rooms/', null=True, blank=True)

    def __str__(self):
        return f"{self.hotel.name} - {self.type_name}"


class Room(models.Model):
    category = models.ForeignKey(RoomCategory, on_delete=models.CASCADE, related_name='rooms')
    room_number = models.CharField(max_length=10)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.category.hotel.name} - Room {self.room_number}"