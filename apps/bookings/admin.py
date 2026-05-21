from django.contrib import admin
from .models import Booking

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    # Admin list view-la ethu theriyanum nu set panrom
    list_display = ('booking_id', 'user', 'room', 'check_in', 'check_out', 'status', 'total_amount')
    # Filter panna (Status, date base pannu)
    list_filter = ('status', 'check_in')
    # Search panna
    search_fields = ('user__username', 'booking_id')
    # Read-only field (booking ID-ai yarum edit panna mudiyathu)
    readonly_fields = ('booking_id', 'created_at')