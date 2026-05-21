from django.urls import path
from . import views
from .views import HotelDetailView
# Use this instead

urlpatterns = [
    path('', views.hotel_list, name='hotel_list'), # Ithu unga Home Page (hotel_list.html)
    path('hotels/', views.explore_hotels, name='explore_hotels'), # 🆕 Ithu namma puthu Hotels page
    path('hotel/<int:pk>/', HotelDetailView.as_view(), name='hotel_detail'),
 

    path('admin-dashboard/', views.custom_admin_dashboard, name='custom_admin_dashboard'),
    path('admin-dashboard/rooms/', views.admin_manage_rooms, name='admin_manage_rooms'),
    path('admin-dashboard/categories/', views.admin_manage_categories, name='admin_manage_categories'),
    path('admin-dashboard/reports/', views.admin_revenue_reports, name='admin_revenue_reports'),
    path('admin-dashboard/reports/pdf/', views.export_revenue_pdf, name='export_revenue_pdf'),
]