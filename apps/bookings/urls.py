from django.urls import path
from .views import BookRoomView, BookingSuccessView, CheckoutView, UserDashboardView, CancelBookingView, ViewBillView # Import CancelView
from apps.bookings.views import LoginRedirectView
urlpatterns = [
    path('book/<int:category_id>/', BookRoomView.as_view(), name='book_room'),
    path('dashboard/', UserDashboardView.as_view(), name='user_dashboard'),
    path('cancel/<int:booking_id>/', CancelBookingView.as_view(), name='cancel_booking'), # New Cancel Route
    path('checkout/<int:booking_id>/', CheckoutView.as_view(), name='checkout'),
    path('success/<int:booking_id>/', BookingSuccessView.as_view(), name='booking_success'),
    path('bill/<int:booking_id>/', ViewBillView.as_view(), name='view_bill'),
    path('login-redirect/', LoginRedirectView.as_view(), name='login_redirect'),
]