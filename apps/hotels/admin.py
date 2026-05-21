from django.contrib import admin
from .models import Hotel, RoomCategory, Room

class RoomCategoryInline(admin.TabularInline):
    model = RoomCategory
    extra = 1

@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'star_rating', 'is_popular', 'created_at')
    list_filter = ('location', 'star_rating', 'is_popular', 'has_ac', 'has_pool')
    search_fields = ('name', 'location')
    inlines = [RoomCategoryInline]

@admin.register(RoomCategory)
class RoomCategoryAdmin(admin.ModelAdmin):
    list_display = ('hotel', 'type_name', 'price_per_night', 'capacity')

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('room_number', 'category', 'is_available')
    list_filter = ('is_available', 'category__hotel')