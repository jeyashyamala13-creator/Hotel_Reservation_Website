import django
from django.shortcuts import render
from django.views import View

# New line (Corrected)
from apps.bookings.models import Booking
# Inga Room-ku bathila RoomCategory-a import pannunga
from .models import Hotel, RoomCategory 

from django.shortcuts import render
from django.db.models import Q, Min, Count
from .models import Hotel

def hotel_list(request):
    hotels = Hotel.objects.all()

    # 1. Main Form Search Parameters
    location_query = request.GET.get('location', '').strip()
    check_in = request.GET.get('check_in', '')
    check_out = request.GET.get('check_out', '')
    guests = request.GET.get('guests', '')

    if location_query:
        hotels = hotels.filter(Q(location__icontains=location_query) | Q(name__icontains=location_query))

    # 2. Sidebar Checkbox Filters
    star_rating = request.GET.get('stars')
    has_ac = request.GET.get('ac')
    has_breakfast = request.GET.get('breakfast')
    has_pool = request.GET.get('pool')
    has_parking = request.GET.get('parking')
    max_price = request.GET.get('max_price')

    if star_rating:
        hotels = hotels.filter(star_rating=star_rating)
    if has_ac == 'on':
        hotels = hotels.filter(has_ac=True)
    if has_breakfast == 'on':
        hotels = hotels.filter(has_breakfast=True)
    if has_pool == 'on':
        hotels = hotels.filter(has_pool=True)
    if has_parking == 'on':
        hotels = hotels.filter(has_parking=True)

    # 3. Dynamic Sorting
    sort_by = request.GET.get('sort', 'recommended')
    
    # Process hotels data for custom aggregation and manual rendering steps if needed
    # Annotating minimum price to cleanly sort down database levels
    hotels = hotels.annotate(min_room_price=Min('categories__price_per_night'))

    if max_price:
        hotels = hotels.filter(min_room_price__lte=max_price)

    if sort_by == 'price_low':
        hotels = hotels.order_by('min_room_price')
    elif sort_by == 'price_high':
        hotels = hotels.order_by('-min_room_price')
    elif sort_by == 'rating':
        hotels = hotels.order_by('-star_rating')
    
    # Separating trending logic elements
    popular_hotels = Hotel.objects.filter(is_popular=True)[:3]
    room_categories = RoomCategory.objects.all()[:4]

    context = {
        'hotels': hotels,
        'popular_hotels': popular_hotels,
        'room_categories': room_categories,
        'filters': request.GET, # Keeps fields active inside UI layout components
    }
    return render(request, 'hotels/hotel_list.html', context)
    
from django.views.generic import DetailView

class HotelDetailView(DetailView):
    model = Hotel
    template_name = 'hotels/hotel_detail.html'
    context_object_name = 'hotel'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # models.py la related_name='categories' nu ulla nala 'categories' nu mathrom
        context['categories'] = self.object.categories.all()
        return context
    
# Unga pazhaya hotel_list matrum HotelDetailView code apdiye irukkatum...

# 🆕 Puthu Dedicated Hotels Page-kana View
def explore_hotels(request):
    hotels = Hotel.objects.all()

    # Location & Date Search
    location_query = request.GET.get('location', '').strip()
    if location_query:
        hotels = hotels.filter(Q(location__icontains=location_query) | Q(name__icontains=location_query))

    # Sidebar Checkbox Filters
    star_rating = request.GET.get('stars')
    has_ac = request.GET.get('ac')
    has_breakfast = request.GET.get('breakfast')
    has_pool = request.GET.get('pool')
    has_parking = request.GET.get('parking')
    max_price = request.GET.get('max_price')

    if star_rating:
        hotels = hotels.filter(star_rating=star_rating)
    if has_ac == 'on':
        hotels = hotels.filter(has_ac=True)
    if has_breakfast == 'on':
        hotels = hotels.filter(has_breakfast=True)
    if has_pool == 'on':
        hotels = hotels.filter(has_pool=True)
    if has_parking == 'on':
        hotels = hotels.filter(has_parking=True)
        
    # Price filtering logic
    hotels = hotels.annotate(min_room_price=Min('categories__price_per_night'))
    if max_price and max_price.isdigit():
        hotels = hotels.filter(min_room_price__lte=int(max_price))

    # Dynamic Sorting Options
    sort_by = request.GET.get('sort', 'recommended')
    if sort_by == 'price_low':
        hotels = hotels.order_by('min_room_price')
    elif sort_by == 'price_high':
        hotels = hotels.order_by('-min_room_price')
    elif sort_by == 'rating':
        hotels = hotels.order_by('-star_rating')
        
    context = {
        'hotels': hotels,
        'filters': request.GET, 
    }
    return render(request, 'hotels/explore_hotels.html', context)    

import io
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.db.models import Sum, Count, Min, Max
from .models import Hotel, RoomCategory, Room

# PDF Generation-ku thevaiyana ReportLab imports
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def custom_admin_dashboard(request):
    # Real-time database stats calculation
    total_hotels = Hotel.objects.count()
    total_categories = RoomCategory.objects.count()
    total_rooms = Room.objects.count()
    available_rooms = Room.objects.filter(is_available=True).count()
    booked_rooms = total_rooms - available_rooms
    
    # Calculating potential total capacity and average prices
    avg_price = RoomCategory.objects.aggregate(avg=Min('price_per_night'))['avg'] or 0
    
    # Chart.js dynamic data from real database
    chart_labels = [cat.type_name for cat in RoomCategory.objects.all()[:7]]
    revenue_data = [float(cat.price_per_night) for cat in RoomCategory.objects.all()[:7]]
    total_bookings = Booking.objects.count()
    pending_bookings = Booking.objects.filter(status='PENDING').count()
    recent_bookings = Booking.objects.all().order_by('-created_at')[:5]

    context = {
        'total_hotels': total_hotels,
        'total_categories': total_categories,
        'total_rooms': total_rooms,
        'available_rooms': available_rooms,
        'booked_rooms': booked_rooms,
        'avg_price': avg_price,
        'chart_labels': chart_labels,
        'revenue_data': revenue_data,
        'active_tab': 'dashboard',
        'total_bookings': total_bookings,
        'pending_bookings': pending_bookings,
        'recent_bookings': recent_bookings,
    }
    return render(request, 'admin/custom_dashboard.html', context)

def admin_manage_rooms(request):
    rooms = Room.objects.select_related('category__hotel').all().order_by('room_number')
    
    # POST request vantha room availability-ah real-time-ah toggle panna logic
    if request.method == "POST":
        room_id = request.POST.get('room_id')
        room = get_object_or_404(Room, id=room_id)
        room.is_available = not room.is_available
        room.save()
        return redirect('admin_manage_rooms')

    context = {
        'rooms': rooms,
        'active_tab': 'rooms'
    }
    return render(request, 'admin/manage_rooms.html', context)

def admin_manage_categories(request):
    categories = RoomCategory.objects.select_related('hotel').all()
    
    if request.method == "POST":
        category_id = request.POST.get('category_id')
        new_price = request.POST.get('price')
        if category_id and new_price:
            category = get_object_or_404(RoomCategory, id=category_id)
            category.price_per_night = new_price
            category.save()
            return redirect('admin_manage_categories')

    context = {
        'categories': categories,
        'active_tab': 'categories'
    }
    return render(request, 'admin/manage_categories.html', context)

def admin_revenue_reports(request):
    categories = RoomCategory.objects.select_related('hotel').all()
    total_value = RoomCategory.objects.aggregate(total=Sum('price_per_night'))['total'] or 0
    max_priced = RoomCategory.objects.aggregate(max_p=Max('price_per_night'))['max_p'] or 0
    
    context = {
        'categories': categories,
        'total_value': total_value,
        'max_priced': max_priced,
        'active_tab': 'reports'
    }
    return render(request, 'admin/revenue_reports.html', context)

def export_revenue_pdf(request):
    # Memory buffer output file set pandrom
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    story = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontSize=24,
        leading=28,
        textColor=colors.HexColor('#111827'),
        spaceAfter=12
    )
    normal_style = styles['Normal']
    
    # PDF Header Elements
    story.append(Paragraph("StayEase Premium - Revenue & Inventory Report", title_style))
    story.append(Paragraph("Generated real-time data directly from application database securely.", normal_style))
    story.append(Spacer(1, 20))
    
    # Table Grid Columns Header
    data = [['Hotel Property', 'Room Category', 'Capacity', 'Price Per Night (INR)']]
    
    categories = RoomCategory.objects.select_related('hotel').all()
    for cat in categories:
        data.append([
            str(cat.hotel.name),
            str(cat.type_name),
            f"{cat.capacity} Guests",
            f"Rs. {cat.price_per_night}"
        ])
    
    # ReportLab Clean Layout Styling
    t = Table(data, colWidths=[150, 150, 100, 130])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#111827')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F9FAFB')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E5E7EB')),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
    ]))
    
    story.append(t)
    doc.build(story)
    
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="StayEase_Revenue_Report.pdf"'
    return response

# apps/hotels/views.py

# apps/hotels/views.py (or whichever file you defined RoleBasedLoginView)
