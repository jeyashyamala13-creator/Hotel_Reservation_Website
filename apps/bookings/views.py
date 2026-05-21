from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin
from apps.hotels.models import Hotel, RoomCategory, Room # Ensure these are correct
from .models import Booking
from .forms import HotelBookingForm
from datetime import datetime

class BookRoomView(LoginRequiredMixin, View):
    def get(self, request, category_id):
        category = get_object_or_404(RoomCategory, id=category_id)
        form = HotelBookingForm()
        return render(request, 'bookings/booking_form.html', {'form': form, 'category': category})

    def post(self, request, category_id):
        category = get_object_or_404(RoomCategory, id=category_id)
        form = HotelBookingForm(request.POST)

        if form.is_valid():
            check_in = form.cleaned_data['check_in']
            check_out = form.cleaned_data['check_out']
            guests = form.cleaned_data['guests']

            # 1. Intha category-la available-ah irukura rooms-ah edukkurom
            rooms = Room.objects.filter(category_id=category_id, is_available=True)
            
            available_room = None
            
            # 2. Rooms checking loop (Room clash irukkaa nu mattum check pannum)
            for room in rooms:
                conflicting_bookings = Booking.objects.filter(
                    room=room,
                    status__in=['PENDING', 'CONFIRMED']
                ).filter(
                    Q(check_in__lt=check_out) & Q(check_out__gt=check_in)
                )
                
                # Clash illana, intha room-ah available_room nu eduthutu loop-ah mudichukurom
                if not conflicting_bookings.exists():
                    available_room = room
                    break

            # 3. FOR LOOP-KU VELIYA (OUTSIDE THE LOOP) thaan intha booking creation irukkanum! 👇
            if available_room:
                nights = (check_out - check_in).days
                total_amount = category.price_per_night * nights

                # Booking create pandrom (Status PENDING)
                booking = Booking.objects.create(
                    user=request.user,
                    room=available_room,
                    check_in=check_in,
                    check_out=check_out,
                    guests=guests,
                    total_amount=total_amount,
                    status='PENDING' 
                )
                # Success-ah booking aanathum checkout page-ku redirect aagum!
                return redirect('checkout', booking_id=booking.id)
            else:
                # Loop mudinjum entha room-மே free-ah illana mattum thaan intha error varanum
                messages.error(request, "Sorry! No rooms are currently available in this category for the selected dates.")
        
        # Form invalid-ah irunthalo allathu room kidaikalanaalo intha template thirumba render aagum
        return render(request, 'bookings/booking_form.html', {'form': form, 'category': category})

# --- PUTHU VIEWS KEEZHE ADD PANNUNGA ---

class CheckoutView(LoginRequiredMixin, View):
    def get(self, request, booking_id):
        booking = get_object_or_404(Booking, id=booking_id, user=request.user)
        return render(request, 'bookings/checkout.html', {'booking': booking})

    def post(self, request, booking_id):
        booking = get_object_or_404(Booking, id=booking_id, user=request.user)
        # Payment details receive aagi success aanathum status CONFIRMED nu aagum
        booking.status = 'CONFIRMED'
        booking.save()
        messages.success(request, f"Payment Successful! Booking ID: {booking.booking_id}")
        return redirect('booking_success', booking_id=booking.id)

class BookingSuccessView(LoginRequiredMixin, View):
    def get(self, request, booking_id):
        booking = get_object_or_404(Booking, id=booking_id, user=request.user)
        return render(request, 'bookings/booking_success.html', {'booking': booking})

class ViewBillView(LoginRequiredMixin, View):
    def get(self, request, booking_id):
        booking = get_object_or_404(Booking, id=booking_id, user=request.user)
        nights = (booking.check_out - booking.check_in).days
        return render(request, 'bookings/bill.html', {'booking': booking, 'nights': nights})
        
from django.contrib.auth.mixins import LoginRequiredMixin

class UserDashboardView(LoginRequiredMixin, View):
    login_url = 'login' # User login aagama vantha, intha url-ku redirect aagidum

    def get(self, request):
        # Login aagirukka user-oda bookings-a mattum filter panni edukirom
        # 'order_by('-created_at')' puthusa panna booking-a first-la kaattum
        user_bookings = Booking.objects.filter(user=request.user).order_by('-created_at')
        
        context = {
            'bookings': user_bookings
        }
        return render(request, 'bookings/dashboard.html', context)  

class CancelBookingView(LoginRequiredMixin, View):
    def post(self, request, booking_id):
        # Securing the cancellation: ensure booking belongs to the logged-in user
        booking = get_object_or_404(Booking, id=booking_id, user=request.user)
        
        if booking.status == 'CONFIRMED':
            booking.status = 'CANCELLED'
            booking.save()
            messages.success(request, f"Booking reference {booking.booking_id} has been successfully cancelled.")
        else:
            messages.error(request, "This booking cannot be cancelled or is already processed.")
            
        return redirect('user_dashboard')      
    

class LoginRedirectView(LoginRequiredMixin, View):
    def get(self, request):
        # User superuser (admin)-ah iruntha custom dashboard-ku redirect panrom
        if request.user.is_superuser:
            return redirect('custom_dashboard')  # Unga custom admin dashboard URL name-ah inga podunga
        
        # Normal user-ah iruntha epavum pola avanga dashboard-ku pogum
        else:
            return redirect('user_dashboard')    