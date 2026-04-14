from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from datetime import datetime, timedelta
import os
import uuid
from .views_contact_api import admin_contact_info_api
from .models import (
    Game, GameCategory, CafeItem, CafeCategory, Package, 
    CricketBooking, CricketPricing, BirthdayParty, Testimonial, ContactInquiry,
    GalleryImage, SiteSettings, AdminUser, CafeOrder, CafeOrderItem, ContactInfo,
    Payment, PackageCard, MembershipCard
)
from .forms import CricketBookingForm, BirthdayPartyForm, ContactInquiryForm, AdminLoginForm, CafeOrderForm, PackageForm, ContactInfoForm


def home(request):
    """Home page with all dynamic content"""
    # Get featured games
    games = Game.objects.filter(is_active=True).select_related('category')
    popular_games = games.filter(is_popular=True)[:3]
    
    # Get cafe items
    cafe_items = CafeItem.objects.filter(is_available=True).select_related('category')
    
    # Get packages
    packages = Package.objects.filter(is_active=True).order_by('price')
    
    # Get testimonials
    testimonials = Testimonial.objects.filter(is_active=True)
    
    # Get gallery images
    gallery_images = GalleryImage.objects.filter(is_active=True)
    
    # Get stats
    stats = {
        'total_games': games.count(),
        'total_packages': packages.count(),
        'total_bookings': CricketBooking.objects.filter(status='confirmed').count(),
        'total_testimonials': testimonials.count(),
    }
    
    context = {
        'games': games,
        'popular_games': popular_games,
        'cafe_items': cafe_items,
        'packages': packages,
        'testimonials': testimonials,
        'gallery_images': gallery_images,
        'stats': stats,
        'site_settings': get_site_settings(),
    }
    return render(request, 'arena/home.html', context)


def games(request):
    """Games listing page"""
    category_filter = request.GET.get('category')
    games = Game.objects.filter(is_active=True).select_related('category')
    
    if category_filter:
        games = games.filter(category__name=category_filter)
    
    categories = GameCategory.objects.all()
    
    context = {
        'games': games,
        'categories': categories,
        'selected_category': category_filter,
        'site_settings': get_site_settings(),
    }
    return render(request, 'arena/games.html', context)


def packages(request):
    """Packages listing page"""
    packages = Package.objects.filter(is_active=True).order_by('price')
    
    context = {
        'packages': packages,
        'site_settings': get_site_settings(),
    }
    return render(request, 'arena/packages_clean.html', context)


def cafe(request):
    """Cafe menu page with cart functionality"""
    category_filter = request.GET.get('category', 'All')
    cafe_items = CafeItem.objects.filter(is_available=True).select_related('category')
    
    if category_filter != 'All':
        cafe_items = cafe_items.filter(category__name=category_filter)
    
    categories = CafeCategory.objects.all()
    
    # Get cart from session
    cart = request.session.get('cafe_cart', {})
    cart_items = []
    total_amount = 0
    
    if cart:
        item_ids = cart.keys()
        cart_items_data = CafeItem.objects.filter(id__in=item_ids, is_available=True)
        
        for item in cart_items_data:
            quantity = cart.get(str(item.id), 0)
            if quantity > 0:
                subtotal = item.price * quantity
                cart_items.append({
                    'item': item,
                    'quantity': quantity,
                    'subtotal': subtotal
                })
                total_amount += subtotal
    
    context = {
        'cafe_items': cafe_items,
        'categories': categories,
        'selected_category': category_filter,
        'cart_items': cart_items,
        'total_amount': total_amount,
        'cart_count': len(cart_items),
        'site_settings': get_site_settings(),
    }
    return render(request, 'arena/cafe.html', context)


def birthday(request):
    """Birthday party booking page"""
    if request.method == 'POST':
        form = BirthdayPartyForm(request.POST)
        if form.is_valid():
            party = form.save()
            messages.success(request, f'Party inquiry submitted! Your party ID is {party.party_id}')
            # Send email notification
            try:
                send_mail(
                    'Birthday Party Inquiry - Happy Hoopers',
                    f'Thank you for your inquiry! Party ID: {party.party_id}',
                    settings.DEFAULT_FROM_EMAIL,
                    [party.email],
                    fail_silently=True,
                )
            except:
                pass
            return redirect('birthday')
    else:
        form = BirthdayPartyForm()
    
    packages = Package.objects.filter(is_active=True)
    
    context = {
        'form': form,
        'packages': packages,
        'site_settings': get_site_settings(),
    }
    return render(request, 'arena/birthday.html', context)


def cricket_booking(request):
    """Cricket booking page with proper slot management"""
    if request.method == 'POST':
        form = CricketBookingForm(request.POST)
        if form.is_valid():
            booking = form.save()
            messages.success(request, f'Booking confirmed! Your booking ID is {booking.booking_id}')
            
            # Send email notification
            try:
                send_mail(
                    'Cricket Booking Confirmed - Happy Hoopers',
                    f'Your booking is confirmed!\n\nBooking ID: {booking.booking_id}\nDate: {booking.date}\nTime: {booking.start_time} - {booking.end_time}\nCost: ₹{booking.cost}',
                    settings.DEFAULT_FROM_EMAIL,
                    [booking.email],
                    fail_silently=True,
                )
            except:
                pass
            return redirect('arena:cricket_booking')
    else:
        form = CricketBookingForm()
    
    # Get available slots for today and next 7 days
    from datetime import date, timedelta
    today = date.today()
    available_dates = [(today + timedelta(days=i)) for i in range(8)]
    
    # Get pricing information
    pricing_slots = CricketPricing.objects.filter(is_active=True).order_by('start_time')
    
    # Get booked slots for selected date
    selected_date = request.GET.get('date', str(today))
    booked_slots = CricketBooking.objects.filter(
        date=selected_date,
        status='confirmed'
    ).values_list('start_time', 'end_time')
    
    context = {
        'form': form,
        'available_dates': available_dates,
        'pricing_slots': pricing_slots,
        'booked_slots': list(booked_slots),
        'selected_date': selected_date,
        'site_settings': get_site_settings(),
    }
    return render(request, 'arena/cricket_booking.html', context)


def gallery(request):
    """Gallery page"""
    category_filter = request.GET.get('category', 'All')
    gallery_images = GalleryImage.objects.filter(is_active=True)
    
    if category_filter != 'All':
        gallery_images = gallery_images.filter(category=category_filter)
    
    # Get categories from the model field choices
    categories = GalleryImage._meta.get_field('category').choices
    
    context = {
        'gallery_images': gallery_images,
        'categories': categories,
        'selected_category': category_filter,
        'site_settings': get_site_settings(),
    }
    return render(request, 'arena/gallery.html', context)


def contact(request):
    """Contact page"""
    if request.method == 'POST':
        form = ContactInquiryForm(request.POST)
        if form.is_valid():
            inquiry = form.save()
            messages.success(request, 'Your inquiry has been submitted. We\'ll contact you soon!')
            # Send email notification
            try:
                send_mail(
                    f'Contact Inquiry: {inquiry.subject}',
                    f'New inquiry from {inquiry.name}: {inquiry.message}',
                    settings.DEFAULT_FROM_EMAIL,
                    [settings.ADMIN_EMAIL],
                    fail_silently=True,
                )
            except:
                pass
            return redirect('arena:contact')
    else:
        form = ContactInquiryForm()
    
    context = {
        'form': form,
        'site_settings': get_site_settings(),
    }
    return render(request, 'arena/contact.html', context)


def about(request):
    """About page"""
    context = {
        'site_settings': get_site_settings(),
    }
    return render(request, 'arena/about.html', context)


# AJAX Views
@csrf_exempt
@require_POST
def check_cricket_availability(request):
    """Check available time slots for cricket booking"""
    date = request.POST.get('date')
    start_time = request.POST.get('start_time')
    end_time = request.POST.get('end_time')
    
    if not date:
        return JsonResponse({'error': 'Date is required'})
    
    if start_time and end_time:
        # Check for specific booking conflict
        try:
            from datetime import datetime
            start_dt = datetime.strptime(f"{date} {start_time}", "%Y-%m-%d %H:%M").time()
            end_dt = datetime.strptime(f"{date} {end_time}", "%Y-%m-%d %H:%M").time()
            
            # Check if this time slot conflicts with existing bookings
            conflicting_bookings = CricketBooking.objects.filter(
                date=date,
                status='confirmed',
                start_time__lt=end_dt,
                end_time__gt=start_dt
            )
            
            if conflicting_bookings.exists():
                return JsonResponse({'conflict': True, 'message': 'This time slot is already booked'})
            else:
                return JsonResponse({'conflict': False, 'message': 'Time slot available'})
                
        except ValueError:
            return JsonResponse({'error': 'Invalid time format'})
    
    # Get all confirmed bookings for the date
    booked_slots = CricketBooking.objects.filter(
        date=date,
        status='confirmed'
    ).values_list('start_time', 'end_time')
    
    # Generate available slots (15-minute intervals from 8 AM to 10 PM)
    available_slots = []
    for hour in range(8, 22):  # 8 AM to 10 PM
        for minute in [0, 15, 30, 45]:
            slot_time = f"{hour:02d}:{minute:02d}"
            
            # Check if this slot is booked
            is_booked = False
            for booked_start, booked_end in booked_slots:
                if (booked_start <= slot_time < booked_end) or \
                   (booked_start < slot_time <= booked_end):
                    is_booked = True
                    break
            
            if not is_booked:
                available_slots.append(slot_time)
    
    return JsonResponse({'available_slots': available_slots})


@csrf_exempt
def add_to_cart(request):
    """Add item to cart"""
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        quantity = int(request.POST.get('quantity', 1))
        
        try:
            item = CafeItem.objects.get(id=item_id, is_available=True)
            
            # Get or create cart
            cart = request.session.get('cafe_cart', {})
            
            # Add/update item in cart
            current_quantity = cart.get(str(item_id), 0)
            new_quantity = current_quantity + quantity
            
            # Check stock
            if new_quantity <= item.stock_quantity:
                cart[str(item_id)] = new_quantity
                request.session['cafe_cart'] = cart
                
                return JsonResponse({
                    'success': True,
                    'message': f'{item.name} added to cart',
                    'cart_count': len(cart),
                    'total_items': sum(cart.values())
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': f'Only {item.stock_quantity} items available in stock'
                })
                
        except CafeItem.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Item not found'})
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})


@csrf_exempt
def update_cart(request):
    """Update cart item quantity"""
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        quantity = int(request.POST.get('quantity', 0))
        
        try:
            item = CafeItem.objects.get(id=item_id, is_available=True)
            
            cart = request.session.get('cafe_cart', {})
            
            if quantity > 0:
                if quantity <= item.stock_quantity:
                    cart[str(item_id)] = quantity
                else:
                    return JsonResponse({
                        'success': False,
                        'message': f'Only {item.stock_quantity} items available in stock'
                    })
            else:
                # Remove item from cart
                cart.pop(str(item_id), None)
            
            request.session['cafe_cart'] = cart
            
            # Calculate new totals
            cart_items_data = CafeItem.objects.filter(id__in=cart.keys(), is_available=True)
            total_amount = sum(item.price * cart.get(str(item.id), 0) for item in cart_items_data)
            
            return JsonResponse({
                'success': True,
                'total_amount': total_amount,
                'cart_count': len(cart),
                'total_items': sum(cart.values())
            })
            
        except CafeItem.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Item not found'})
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})


def clear_cart(request):
    """Clear entire cart"""
    request.session['cafe_cart'] = {}
    return JsonResponse({'success': True, 'message': 'Cart cleared'})


def place_order(request):
    """Place cafe order"""
    if request.method == 'POST':
        form = CafeOrderForm(request.POST)
        
        # Get cart data from form submission
        cart_data = {}
        for key, value in request.POST.items():
            if key.startswith('cart_item_'):
                item_id = key.replace('cart_item_', '')
                cart_data[item_id] = int(value)
        
        if not cart_data:
            messages.error(request, 'Your cart is empty!')
            return redirect('arena:cafe')
        
        if form.is_valid():
            try:
                # Calculate total amount and validate stock
                total_amount = 0
                cart_items_data = []
                
                for item_id, quantity in cart_data.items():
                    try:
                        item = CafeItem.objects.get(id=item_id, is_available=True)
                        
                        # Check stock
                        if quantity > item.stock_quantity:
                            messages.error(request, f'Only {item.stock_quantity} {item.name} available in stock!')
                            return redirect('arena:cafe')
                        
                        subtotal = item.price * quantity
                        total_amount += subtotal
                        
                        cart_items_data.append({
                            'item': item,
                            'quantity': quantity,
                            'price_per_item': item.price,
                            'subtotal': subtotal
                        })
                    except CafeItem.DoesNotExist:
                        messages.error(request, 'Some items in your cart are no longer available!')
                        return redirect('arena:cafe')
                
                # Create order
                order = CafeOrder.objects.create(
                    customer_name=form.cleaned_data['customer_name'],
                    mobile=form.cleaned_data['mobile'],
                    table_number=form.cleaned_data['table_number'],
                    total_amount=total_amount,
                    notes=form.cleaned_data.get('notes', '')
                )
                
                # Create order items and update stock
                for cart_item in cart_items_data:
                    CafeOrderItem.objects.create(
                        order=order,
                        cafe_item=cart_item['item'],
                        quantity=cart_item['quantity'],
                        price_per_item=cart_item['price_per_item']
                    )
                    
                    # Update stock
                    item = cart_item['item']
                    item.stock_quantity -= cart_item['quantity']
                    item.save()
                
                # Clear cart from session
                request.session['cafe_cart'] = {}
                
                # Send notification to admin
                try:
                    send_mail(
                        f'New Cafe Order - {order.order_id}',
                        f'New order received:\n\nOrder ID: {order.order_id}\nCustomer: {order.customer_name}\nMobile: {order.mobile}\nTable: {order.table_number}\nAmount: ₹{order.total_amount}',
                        settings.DEFAULT_FROM_EMAIL,
                        [settings.ADMIN_EMAIL],
                        fail_silently=True,
                    )
                except:
                    pass
                
                messages.success(request, f'Order placed successfully! Your order ID is {order.order_id}. Admin will confirm your order soon.')
                return redirect('arena:cafe')
                
            except Exception as e:
                messages.error(request, 'There was an error placing your order. Please try again.')
        else:
            messages.error(request, 'Please correct the errors in the form.')
    
    else:
        form = CafeOrderForm()
    
    # Get cart items for display (from session)
    cart = request.session.get('cafe_cart', {})
    cart_items = []
    total_amount = 0
    
    if cart:
        item_ids = cart.keys()
        cart_items_data = CafeItem.objects.filter(id__in=item_ids, is_available=True)
        
        for item in cart_items_data:
            quantity = cart.get(str(item.id), 0)
            if quantity > 0:
                subtotal = item.price * quantity
                cart_items.append({
                    'item': item,
                    'quantity': quantity,
                    'subtotal': subtotal
                })
                total_amount += subtotal
    
    context = {
        'form': form,
        'cart_items': cart_items,
        'total_amount': total_amount,
        'site_settings': get_site_settings(),
    }
    return render(request, 'arena/place_order.html', context)


@csrf_exempt
def admin_cricket_bookings_api(request):
    """API for cricket booking management"""
    if request.method == 'GET':
        status_filter = request.GET.get('status')
        bookings = CricketBooking.objects.all()
        
        if status_filter and status_filter != 'all':
            bookings = bookings.filter(status=status_filter)
        
        bookings = bookings.order_by('-created_at')
        
        bookings_data = []
        for booking in bookings:
            bookings_data.append({
                'id': booking.id,
                'booking_id': booking.booking_id,
                'name': booking.name,
                'mobile': booking.mobile,
                'email': booking.email,
                'date': str(booking.date),
                'start_time': str(booking.start_time),
                'end_time': str(booking.end_time),
                'duration_minutes': booking.duration_minutes,
                'cost': float(booking.cost),
                'status': booking.status,
                'notes': booking.notes,
                'created_at': booking.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            })
        
        return JsonResponse({'bookings': bookings_data})
    
    elif request.method == 'PUT':
        try:
            data = json.loads(request.body)
            booking_id = data.get('id')
            status = data.get('status')
            
            if not booking_id or not status:
                return JsonResponse({'success': False, 'message': 'ID and status required'})
            
            booking = CricketBooking.objects.get(id=booking_id)
            booking.status = status
            booking.save()
            
            return JsonResponse({'success': True, 'message': 'Booking updated successfully'})
        except CricketBooking.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Booking not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    elif request.method == 'DELETE':
        try:
            data = json.loads(request.body)
            booking_id = data.get('id')
            
            if not booking_id:
                return JsonResponse({'success': False, 'message': 'ID required'})
            
            booking = CricketBooking.objects.get(id=booking_id)
            booking.delete()
            
            return JsonResponse({'success': True, 'message': 'Booking deleted successfully'})
        except CricketBooking.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Booking not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})


@csrf_exempt
def admin_cafe_orders_api(request):
    """API for cafe order management"""
    if request.method == 'GET':
        status_filter = request.GET.get('status')
        orders = CafeOrder.objects.all().prefetch_related('items__cafe_item')
        
        if status_filter and status_filter != 'all':
            orders = orders.filter(status=status_filter)
        
        orders = orders.order_by('-created_at')
        
        orders_data = []
        for order in orders:
            order_items = []
            for item in order.items.all():
                order_items.append({
                    'item_name': item.cafe_item.name,
                    'quantity': item.quantity,
                    'price_per_item': float(item.price_per_item),
                    'subtotal': float(item.subtotal)
                })
            
            orders_data.append({
                'id': order.id,
                'order_id': order.order_id,
                'customer_name': order.customer_name,
                'mobile': order.mobile,
                'table_number': order.table_number,
                'total_amount': float(order.total_amount),
                'status': order.status,
                'notes': order.notes,
                'date': order.created_at.strftime('%Y-%m-%d'),
                'items_count': order.items.count(),
                'order_items': order_items
            })
        
        return JsonResponse({'orders': orders_data})
    
    elif request.method == 'PUT':
        try:
            data = json.loads(request.body)
            order_id = data.get('id')
            status = data.get('status')
            
            if not order_id or not status:
                return JsonResponse({'success': False, 'message': 'ID and status required'})
            
            order = CafeOrder.objects.get(id=order_id)
            order.status = status
            order.save()
            
            return JsonResponse({'success': True, 'message': 'Order updated successfully'})
        except CafeOrder.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Order not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    elif request.method == 'DELETE':
        try:
            data = json.loads(request.body)
            order_id = data.get('id')
            
            if not order_id:
                return JsonResponse({'success': False, 'message': 'ID required'})
            
            order = CafeOrder.objects.get(id=order_id)
            order.delete()
            
            return JsonResponse({'success': True, 'message': 'Order deleted successfully'})
        except CafeOrder.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Order not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})


@csrf_exempt
def admin_cricket_pricing_api(request):
    """API for cricket pricing management"""
    if request.method == 'GET':
        pricing = CricketPricing.objects.all().order_by('start_time')
        
        pricing_data = []
        for rule in pricing:
            pricing_data.append({
                'id': rule.id,
                'name': rule.name,
                'start_time': str(rule.start_time),
                'end_time': str(rule.end_time),
                'price_per_slot': float(rule.price_per_slot),
                'days_applicable': rule.days_applicable,
                'is_active': rule.is_active,
                'created_at': rule.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            })
        
        return JsonResponse({'pricing': pricing_data})
    
    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            pricing = CricketPricing.objects.create(
                name=data.get('name'),
                start_time=data.get('start_time'),
                end_time=data.get('end_time'),
                price_per_slot=data.get('price_per_slot'),
                days_applicable=data.get('days_applicable'),
                is_active=data.get('is_active', True),
            )
            
            return JsonResponse({'success': True, 'message': 'Pricing rule created successfully'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    elif request.method == 'PUT':
        try:
            data = json.loads(request.body)
            pricing_id = data.get('id')
            
            if not pricing_id:
                return JsonResponse({'success': False, 'message': 'ID required'})
            
            pricing = CricketPricing.objects.get(id=pricing_id)
            
            pricing.name = data.get('name', pricing.name)
            pricing.start_time = data.get('start_time', pricing.start_time)
            pricing.end_time = data.get('end_time', pricing.end_time)
            pricing.price_per_slot = data.get('price_per_slot', pricing.price_per_slot)
            pricing.days_applicable = data.get('days_applicable', pricing.days_applicable)
            pricing.is_active = data.get('is_active', pricing.is_active)
            
            pricing.save()
            
            return JsonResponse({'success': True, 'message': 'Pricing rule updated successfully'})
        except CricketPricing.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Pricing rule not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    elif request.method == 'DELETE':
        try:
            data = json.loads(request.body)
            pricing_id = data.get('id')
            
            if not pricing_id:
                return JsonResponse({'success': False, 'message': 'ID required'})
            
            pricing = CricketPricing.objects.get(id=pricing_id)
            pricing.delete()
            
            return JsonResponse({'success': True, 'message': 'Pricing rule deleted successfully'})
        except CricketPricing.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Pricing rule not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})


@csrf_exempt
@require_POST
def update_cafe_stock(request):
    """Update cafe item stock (for admin)"""
    item_id = request.POST.get('item_id')
    quantity = request.POST.get('quantity')
    
    if not item_id or not quantity:
        return JsonResponse({'error': 'Item ID and quantity required'})
    
    try:
        item = CafeItem.objects.get(id=item_id)
        item.stock_quantity = int(quantity)
        item.save()
        return JsonResponse({'success': True, 'new_quantity': item.stock_quantity})
    except CafeItem.DoesNotExist:
        return JsonResponse({'error': 'Item not found'})


# API Views for dynamic content
def api_games(request):
    """API endpoint for games data"""
    games = Game.objects.filter(is_active=True).select_related('category').values(
        'id', 'name', 'category__name', 'category__emoji', 'description',
        'duration', 'age_group', 'price_info', 'image_url', 'is_popular'
    )
    return JsonResponse(list(games), safe=False)


def api_cafe_items(request):
    """API endpoint for cafe items data"""
    category = request.GET.get('category')
    items = CafeItem.objects.filter(is_available=True)
    
    if category and category != 'All':
        items = items.filter(category__name=category)
    
    items = items.select_related('category').values(
        'id', 'name', 'category__name', 'category__emoji', 'description',
        'price', 'stock_quantity', 'image_url'
    )
    return JsonResponse(list(items), safe=False)


def api_packages(request):
    """API endpoint for packages data"""
    packages = Package.objects.filter(is_active=True).values(
        'id', 'name', 'tagline', 'price', 'duration', 'features',
        'color_scheme', 'is_featured'
    )
    return JsonResponse(list(packages), safe=False)


def api_testimonials(request):
    """API endpoint for testimonials data"""
    testimonials = Testimonial.objects.filter(is_active=True).values(
        'id', 'name', 'role', 'rating', 'review_text', 'avatar_emoji'
    ).order_by('order')
    return JsonResponse(list(testimonials), safe=False)


# Helper functions
def get_site_settings():
    """Get site settings as dictionary"""
    settings_dict = {}
    settings_obj = SiteSettings.objects.all()
    for setting in settings_obj:
        settings_dict[setting.key] = setting.value
    return settings_dict


def admin_login(request):
    """Admin login page"""
    if request.user.is_authenticated:
        # Check if user is admin
        try:
            admin_user = AdminUser.objects.get(user=request.user)
            return redirect('arena:admin_dashboard')
        except AdminUser.DoesNotExist:
            logout(request)
    
    if request.method == 'POST':
        form = AdminLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            
            user = authenticate(request, username=username, password=password)
            if user is not None:
                # Check if user is admin
                try:
                    admin_user = AdminUser.objects.get(user=user)
                    login(request, user)
                    admin_user.last_login = timezone.now()
                    admin_user.save()
                    messages.success(request, 'Welcome to admin dashboard!')
                    return redirect('arena:admin_dashboard')
                except AdminUser.DoesNotExist:
                    form.add_error(None, 'You do not have admin privileges.')
            else:
                form.add_error(None, 'Invalid username or password.')
    else:
        form = AdminLoginForm()
    
    return render(request, 'arena/admin_login.html', {'form': form})


@login_required(login_url='arena:admin_login')
def admin_logout(request):
    """Admin logout"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('arena:admin_login')


@login_required(login_url='arena:admin_login')
def admin_dashboard(request):
    """Admin dashboard page with full access"""
    # Get all model counts and recent data
    from django.db.models import Count
    
    # Model counts
    games_count = Game.objects.count()
    categories_count = GameCategory.objects.count()
    packages_count = Package.objects.count()
    featured_packages_count = Package.objects.filter(is_featured=True).count()
    cafe_items_count = CafeItem.objects.count()
    cricket_bookings_count = CricketBooking.objects.count()
    birthday_parties_count = BirthdayParty.objects.count()
    gallery_images_count = GalleryImage.objects.count()
    testimonials_count = Testimonial.objects.count()
    contact_inquiries_count = ContactInquiry.objects.count()
    cafe_orders_count = CafeOrder.objects.count()
    membership_cards_count = MembershipCard.objects.count()
    active_memberships_count = MembershipCard.objects.filter(status='active').count()
    expired_memberships_count = MembershipCard.objects.filter(status='expired').count()
    
    # Recent data
    recent_games = Game.objects.filter(is_active=True).order_by('-created_at')[:5]
    recent_bookings = CricketBooking.objects.all().order_by('-created_at')[:5]
    recent_birthday_parties = BirthdayParty.objects.all().order_by('-created_at')[:5]
    recent_inquiries = ContactInquiry.objects.all().order_by('-created_at')[:5]
    recent_orders = CafeOrder.objects.all().order_by('-created_at')[:5]
    recent_memberships = MembershipCard.objects.all().order_by('-created_at')[:5]
    
    # Status counts
    pending_bookings = CricketBooking.objects.filter(status='pending').count()
    pending_parties = BirthdayParty.objects.filter(status='inquiry').count()
    pending_inquiries = ContactInquiry.objects.filter(is_resolved=False).count()
    pending_orders = CafeOrder.objects.filter(status='pending').count()
    
    # Popular packages
    popular_packages = Package.objects.filter(is_featured=True).order_by('-order')[:3]
    
    # Low stock items
    low_stock_items = CafeItem.objects.filter(stock_quantity__lte=10).order_by('stock_quantity')[:5]
    
    # Get contact info
    contact_info = ContactInfo.get_contact_info()
    
    context = {
        'games_count': games_count,
        'categories_count': categories_count,
        'packages_count': packages_count,
        'featured_packages_count': featured_packages_count,
        'cafe_items_count': cafe_items_count,
        'cricket_bookings_count': cricket_bookings_count,
        'birthday_parties_count': birthday_parties_count,
        'gallery_images_count': gallery_images_count,
        'testimonials_count': testimonials_count,
        'contact_inquiries_count': contact_inquiries_count,
        'cafe_orders_count': cafe_orders_count,
        'membership_cards_count': membership_cards_count,
        'active_memberships_count': active_memberships_count,
        'expired_memberships_count': expired_memberships_count,
        
        'recent_games': recent_games,
        'recent_bookings': recent_bookings,
        'recent_birthday_parties': recent_birthday_parties,
        'recent_inquiries': recent_inquiries,
        'recent_orders': recent_orders,
        'recent_memberships': recent_memberships,
        
        'pending_bookings': pending_bookings,
        'pending_parties': pending_parties,
        'pending_inquiries': pending_inquiries,
        'pending_orders': pending_orders,
        'low_stock_items': low_stock_items,
        'contact_info': contact_info,
        'site_settings': get_site_settings(),
    }
    return render(request, 'arena/admin_dashboard_modular.html', context)


def handler404(request, exception):
    """Custom 404 handler"""
    return render(request, 'arena/404.html', status=404)


def handler500(request):
    """Custom 500 handler"""
    return render(request, 'arena/500.html', status=500)


# Admin API Views
@csrf_exempt
def admin_games_api(request):
    """API for managing games"""
    if request.method == 'GET':
        # Get all games with categories
        games = Game.objects.select_related('category').all().order_by('order', 'name')
        games_data = []
        for game in games:
            games_data.append({
                'id': game.id,
                'name': game.name,
                'category': {
                    'id': game.category.id,
                    'name': game.category.name
                },
                'description': game.description,
                'duration': game.duration,
                'age_group': game.age_group,
                'price_info': game.price_info,
                'package': game.package,
                'image_url': game.image_url,
                'is_popular': game.is_popular,
                'order': game.order,
                'is_active': game.is_active,
                'created_at': game.created_at.strftime('%Y-%m-%d %H:%M')
            })
        return JsonResponse({'games': games_data})
    
    elif request.method == 'POST':
        # Add new game with image upload
        try:
            # Handle both JSON and multipart form data
            if request.content_type.startswith('multipart/form-data'):
                # Handle file upload
                name = request.POST.get('name')
                category_id = request.POST.get('category')
                description = request.POST.get('description', '')
                duration = request.POST.get('duration')
                age_group = request.POST.get('age_group')
                price_info = request.POST.get('price_info')
                package = request.POST.get('package')
                image_url = request.POST.get('image_url', '')
                is_popular = request.POST.get('is_popular') == 'on' or request.POST.get('is_popular') == 'true'
                order = int(request.POST.get('order', 0))
                is_active = request.POST.get('is_active', 'True') == 'True'
                
                # Handle image file upload
                image_file = request.FILES.get('image')
                if image_file:
                    # Debug: Log file info
                    print(f"Image file received: {image_file.name}")
                    print(f"Image file size: {image_file.size}")
                    print(f"Image file content type: {image_file.content_type}")
                    
                    # Create unique filename
                    file_extension = os.path.splitext(image_file.name)[1]
                    unique_filename = f"game_{uuid.uuid4().hex[:8]}{file_extension}"
                    
                    # Create games directory if it doesn't exist
                    games_dir = os.path.join(settings.MEDIA_ROOT, 'games')
                    os.makedirs(games_dir, exist_ok=True)
                    
                    # Save file
                    file_path = os.path.join(games_dir, unique_filename)
                    with open(file_path, 'wb') as f:
                        for chunk in image_file.chunks():
                            f.write(chunk)
                    
                    # Debug: Log saved file path
                    print(f"File saved to: {file_path}")
                    print(f"File exists: {os.path.exists(file_path)}")
                    
                    # Set image URL
                    image_url = f"{settings.MEDIA_URL}games/{unique_filename}"
                    print(f"Image URL: {image_url}")
                else:
                    print("No image file received in request.FILES")
                    print(f"Request FILES: {dict(request.FILES)}")
                    print(f"Request POST keys: {list(request.POST.keys())}")
                
            else:
                # Handle JSON data
                data = json.loads(request.body)
                name = data['name']
                category_id = data['category']
                description = data.get('description', '')
                duration = data['duration']
                age_group = data['age_group']
                price_info = data['price_info']
                package = data['package']
                image_url = data.get('image_url', '')
                is_popular = data.get('is_popular', False)
                order = data.get('order', 0)
                is_active = data.get('is_active', True)
            
            # Validate required fields
            if not all([name, category_id, duration, age_group, price_info, package]):
                return JsonResponse({
                    'success': False,
                    'message': 'Missing required fields'
                }, status=400)
            
            # Get category
            category = GameCategory.objects.get(id=category_id)
            
            # Create game
            game = Game.objects.create(
                name=name,
                category=category,
                description=description,
                duration=duration,
                age_group=age_group,
                price_info=price_info,
                package=package,
                image_url=image_url,
                is_popular=is_popular,
                order=order,
                is_active=is_active
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Game added successfully!',
                'game': {
                    'id': game.id,
                    'name': game.name,
                    'duration': game.duration,
                    'age_group': game.age_group,
                    'image_url': game.image_url
                }
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=400)
    
    elif request.method == 'PUT':
        # Update existing game
        try:
            data = json.loads(request.body)
            game_id = data.get('id')
            game = Game.objects.get(id=game_id)
            
            if 'category' in data:
                game.category = GameCategory.objects.get(id=data['category'])
            
            game.name = data.get('name', game.name)
            game.description = data.get('description', game.description)
            game.duration = data.get('duration', game.duration)
            game.age_group = data.get('age_group', game.age_group)
            game.price_info = data.get('price_info', game.price_info)
            game.package = data.get('package', game.package)
            game.image_url = data.get('image_url', game.image_url)
            game.is_popular = data.get('is_popular', game.is_popular)
            game.order = data.get('order', game.order)
            game.is_active = data.get('is_active', game.is_active)
            
            game.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Game updated successfully!',
                'game': {
                    'id': game.id,
                    'name': game.name,
                    'duration': game.duration,
                    'age_group': game.age_group,
                    'image_url': game.image_url
                }
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=400)
    
    elif request.method == 'DELETE':
        # Delete game
        try:
            data = json.loads(request.body)
            game_id = data.get('id')
            game = Game.objects.get(id=game_id)
            
            # Delete image file if exists
            if game.image_url and game.image_url.startswith(settings.MEDIA_URL):
                image_path = os.path.join(settings.MEDIA_ROOT, game.image_url.replace(settings.MEDIA_URL, ''))
                if os.path.exists(image_path):
                    os.remove(image_path)
            
            game.delete()
            
            return JsonResponse({
                'success': True,
                'message': 'Game deleted successfully!'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=400)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@csrf_exempt
def admin_cafe_categories_api(request):
    """API for listing cafe categories (used by admin dashboard forms)."""
    if request.method == 'GET':
        categories = CafeCategory.objects.all().order_by('name')
        categories_data = []
        for category in categories:
            categories_data.append({
                'id': category.id,
                'name': category.name,
                'emoji': category.emoji,
                'tag_class': category.tag_class,
            })
        return JsonResponse({'categories': categories_data})

    return JsonResponse({'error': 'Method not allowed'}, status=405)


@csrf_exempt
def admin_cafe_items_api(request):
    """API for managing cafe items."""
    if request.method == 'GET':
        items = CafeItem.objects.select_related('category').all().order_by('order', 'name')
        items_data = []
        for item in items:
            items_data.append({
                'id': item.id,
                'name': item.name,
                'category': {
                    'id': item.category.id,
                    'name': item.category.name,
                },
                'description': item.description,
                'price': float(item.price),
                'stock_quantity': item.stock_quantity,
                'image_url': item.image_url,
                'image': item.image.url if item.image else '',
                'is_available': item.is_available,
                'order': item.order,
                'created_at': item.created_at.strftime('%Y-%m-%d %H:%M'),
            })
        return JsonResponse({'items': items_data})

    elif request.method == 'POST':
        try:
            # Handle both JSON and multipart form data
            if request.content_type.startswith('multipart/form-data'):
                name = request.POST.get('name')
                category_id = request.POST.get('category')
                price = request.POST.get('price')
                description = request.POST.get('description', '')
                stock_quantity = request.POST.get('stock_quantity', '0')
                is_available = request.POST.get('is_available') == 'on'
                order = request.POST.get('order', '0')
                image_url = request.POST.get('image_url', '')

                image_file = request.FILES.get('image')
                if image_file:
                    import os, uuid
                    from django.conf import settings
                    
                    file_extension = os.path.splitext(image_file.name)[1]
                    unique_filename = f"cafe_{uuid.uuid4().hex[:8]}{file_extension}"
                    
                    cafe_dir = os.path.join(settings.MEDIA_ROOT, 'cafe')
                    os.makedirs(cafe_dir, exist_ok=True)
                    
                    file_path = os.path.join(cafe_dir, unique_filename)
                    with open(file_path, 'wb') as f:
                        for chunk in image_file.chunks():
                            f.write(chunk)
                    
                    image_url = f"{settings.MEDIA_URL}cafe/{unique_filename}"
            else:
                data = json.loads(request.body)
                name = data.get('name')
                category_id = data.get('category')
                price = data.get('price')
                description = data.get('description', '')
                stock_quantity = data.get('stock_quantity', 0)
                is_available = data.get('is_available', True)
                order = data.get('order', 0)
                image_url = data.get('image_url', '')

            if not all([name, category_id, price is not None]):
                return JsonResponse({
                    'success': False,
                    'message': 'Missing required fields'
                }, status=400)

            category = CafeCategory.objects.get(id=category_id)

            item = CafeItem.objects.create(
                name=name,
                category=category,
                description=description,
                price=price,
                stock_quantity=int(stock_quantity) or 0,
                image_url=image_url,
                is_available=is_available,
                order=int(order) or 0,
            )

            return JsonResponse({
                'success': True,
                'message': 'Cafe item added successfully!',
                'item': {
                    'id': item.id,
                    'name': item.name,
                    'price': float(item.price),
                    'image_url': item.image_url,
                }
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=400)

    elif request.method == 'PUT':
        try:
            # Handle both JSON and multipart form data
            if request.content_type.startswith('multipart/form-data'):
                item_id = request.POST.get('id')
                item = CafeItem.objects.get(id=item_id)

                if request.POST.get('category'):
                    item.category = CafeCategory.objects.get(id=request.POST.get('category'))

                if 'name' in request.POST:
                    item.name = request.POST.get('name')
                if 'description' in request.POST:
                    item.description = request.POST.get('description')
                if 'price' in request.POST:
                    item.price = float(request.POST.get('price'))
                if 'stock_quantity' in request.POST:
                    item.stock_quantity = int(request.POST.get('stock_quantity') or 0)
                if 'is_available' in request.POST:
                    item.is_available = request.POST.get('is_available') == 'on'
                if 'order' in request.POST:
                    item.order = int(request.POST.get('order') or 0)

                image_file = request.FILES.get('image')
                if image_file:
                    import os, uuid
                    from django.conf import settings
                    
                    file_extension = os.path.splitext(image_file.name)[1]
                    unique_filename = f"cafe_{uuid.uuid4().hex[:8]}{file_extension}"
                    
                    cafe_dir = os.path.join(settings.MEDIA_ROOT, 'cafe')
                    os.makedirs(cafe_dir, exist_ok=True)
                    
                    file_path = os.path.join(cafe_dir, unique_filename)
                    with open(file_path, 'wb') as f:
                        for chunk in image_file.chunks():
                            f.write(chunk)
                    
                    item.image_url = f"{settings.MEDIA_URL}cafe/{unique_filename}"
                elif 'image_url' in request.POST:
                    item.image_url = request.POST.get('image_url') or ''

                item.save()
            else:
                data = json.loads(request.body)
                item_id = data.get('id')
                item = CafeItem.objects.get(id=item_id)

                if 'category' in data and data.get('category'):
                    item.category = CafeCategory.objects.get(id=data['category'])

                if 'name' in data:
                    item.name = data.get('name', item.name)
                if 'description' in data:
                    item.description = data.get('description', item.description)
                if 'price' in data:
                    item.price = data.get('price', item.price)
                if 'stock_quantity' in data:
                    item.stock_quantity = data.get('stock_quantity', item.stock_quantity)
                if 'image_url' in data:
                    item.image_url = data.get('image_url') or ''
                if 'is_available' in data:
                    item.is_available = data.get('is_available', item.is_available)
                if 'order' in data:
                    item.order = data.get('order', item.order)

                item.save()

            return JsonResponse({
                'success': True,
                'message': 'Cafe item updated successfully!',
                'item': {
                    'id': item.id,
                    'name': item.name,
                    'price': float(item.price),
                    'image_url': item.image_url,
                }
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=400)

    elif request.method == 'DELETE':
        try:
            data = json.loads(request.body)
            item_id = data.get('id')
            item = CafeItem.objects.get(id=item_id)
            item.delete()

            return JsonResponse({
                'success': True,
                'message': 'Cafe item deleted successfully!'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=400)

    return JsonResponse({'error': 'Method not allowed'}, status=405)


@csrf_exempt
def admin_gallery_api(request):
    """API for managing gallery images"""
    if request.method == 'GET':
        images = GalleryImage.objects.all().order_by('order', '-created_at')
        images_data = []
        for img in images:
            images_data.append({
                'id': img.id,
                'title': img.title,
                'description': img.description,
                'image_url': img.image_url,
                'image': img.image.url if img.image else '',
                'category': img.category,
                'is_active': img.is_active,
                'order': img.order,
                'created_at': img.created_at.strftime('%Y-%m-%d %H:%M'),
            })
        return JsonResponse({'images': images_data})

    elif request.method == 'POST':
        try:
            # Handle both JSON and multipart form data
            if request.content_type.startswith('multipart/form-data'):
                title = request.POST.get('title')
                description = request.POST.get('description', '')
                category = request.POST.get('category')
                is_active = request.POST.get('is_active') == 'on'
                order = request.POST.get('order', '0')
                image_url = request.POST.get('image_url', '')

                image_file = request.FILES.get('image')
                if image_file:
                    import os, uuid
                    from django.conf import settings
                    
                    file_extension = os.path.splitext(image_file.name)[1]
                    unique_filename = f"gallery_{uuid.uuid4().hex[:8]}{file_extension}"
                    
                    gallery_dir = os.path.join(settings.MEDIA_ROOT, 'gallery')
                    os.makedirs(gallery_dir, exist_ok=True)
                    
                    file_path = os.path.join(gallery_dir, unique_filename)
                    with open(file_path, 'wb') as f:
                        for chunk in image_file.chunks():
                            f.write(chunk)
                    
                    image_url = f"{settings.MEDIA_URL}gallery/{unique_filename}"
            else:
                data = json.loads(request.body)
                title = data.get('title')
                description = data.get('description', '')
                category = data.get('category')
                is_active = data.get('is_active', True)
                order = data.get('order', 0)
                image_url = data.get('image_url', '')

            if not all([title, category]):
                return JsonResponse({
                    'success': False,
                    'message': 'Title and category are required'
                }, status=400)

            image = GalleryImage.objects.create(
                title=title,
                description=description,
                category=category,
                image_url=image_url,
                is_active=is_active,
                order=int(order) or 0,
            )

            return JsonResponse({
                'success': True,
                'message': 'Gallery image added successfully!',
                'image': {
                    'id': image.id,
                    'title': image.title,
                    'image_url': image.image_url,
                }
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=400)

    elif request.method == 'PUT':
        try:
            # Handle both JSON and multipart form data
            if request.content_type.startswith('multipart/form-data'):
                image_id = request.POST.get('id')
                image = GalleryImage.objects.get(id=image_id)

                if 'title' in request.POST:
                    image.title = request.POST.get('title')
                if 'description' in request.POST:
                    image.description = request.POST.get('description')
                if 'category' in request.POST:
                    image.category = request.POST.get('category')
                if 'is_active' in request.POST:
                    image.is_active = request.POST.get('is_active') == 'on'
                if 'order' in request.POST:
                    image.order = int(request.POST.get('order') or 0)

                image_file = request.FILES.get('image')
                if image_file:
                    import os, uuid
                    from django.conf import settings
                    
                    file_extension = os.path.splitext(image_file.name)[1]
                    unique_filename = f"gallery_{uuid.uuid4().hex[:8]}{file_extension}"
                    
                    gallery_dir = os.path.join(settings.MEDIA_ROOT, 'gallery')
                    os.makedirs(gallery_dir, exist_ok=True)
                    
                    file_path = os.path.join(gallery_dir, unique_filename)
                    with open(file_path, 'wb') as f:
                        for chunk in image_file.chunks():
                            f.write(chunk)
                    
                    image.image_url = f"{settings.MEDIA_URL}gallery/{unique_filename}"
                elif 'image_url' in request.POST:
                    image.image_url = request.POST.get('image_url') or ''

                image.save()
            else:
                data = json.loads(request.body)
                image_id = data.get('id')
                image = GalleryImage.objects.get(id=image_id)

                if 'title' in data:
                    image.title = data.get('title', image.title)
                if 'description' in data:
                    image.description = data.get('description', image.description)
                if 'category' in data:
                    image.category = data.get('category', image.category)
                if 'image_url' in data:
                    image.image_url = data.get('image_url') or ''
                if 'is_active' in data:
                    image.is_active = data.get('is_active', image.is_active)
                if 'order' in data:
                    image.order = data.get('order', image.order)

                image.save()

            return JsonResponse({
                'success': True,
                'message': 'Gallery image updated successfully!',
                'image': {
                    'id': image.id,
                    'title': image.title,
                    'image_url': image.image_url,
                }
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=400)

    elif request.method == 'DELETE':
        try:
            data = json.loads(request.body)
            image_id = data.get('id')
            image = GalleryImage.objects.get(id=image_id)
            image.delete()

            return JsonResponse({
                'success': True,
                'message': 'Gallery image deleted successfully!'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=400)

    return JsonResponse({'error': 'Method not allowed'}, status=405)


@csrf_exempt
def admin_inquiries_api(request):
    """API for managing contact inquiries"""
    if request.method == 'GET':
        inquiries = ContactInquiry.objects.all().order_by('-created_at')
        status_filter = request.GET.get('status')
        
        if status_filter == 'pending':
            inquiries = inquiries.filter(is_resolved=False)
        elif status_filter == 'resolved':
            inquiries = inquiries.filter(is_resolved=True)
        
        inquiries_data = []
        for inquiry in inquiries:
            inquiries_data.append({
                'id': inquiry.id,
                'name': inquiry.name,
                'email': inquiry.email,
                'phone': inquiry.mobile,
                'subject': inquiry.subject,
                'message': inquiry.message,
                'is_resolved': inquiry.is_resolved,
                'created_at': inquiry.created_at.strftime('%Y-%m-%d %H:%M'),
            })
        return JsonResponse({'inquiries': inquiries_data})

    elif request.method == 'PUT':
        try:
            data = json.loads(request.body)
            inquiry_id = data.get('id')
            inquiry = ContactInquiry.objects.get(id=inquiry_id)

            if 'is_resolved' in data:
                inquiry.is_resolved = data.get('is_resolved', inquiry.is_resolved)

            inquiry.save()

            return JsonResponse({
                'success': True,
                'message': 'Inquiry updated successfully!',
                'inquiry': {
                    'id': inquiry.id,
                    'is_resolved': inquiry.is_resolved,
                }
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=400)

    elif request.method == 'DELETE':
        try:
            data = json.loads(request.body)
            inquiry_id = data.get('id')
            inquiry = ContactInquiry.objects.get(id=inquiry_id)
            inquiry.delete()

            return JsonResponse({
                'success': True,
                'message': 'Inquiry deleted successfully!'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=400)

    return JsonResponse({'error': 'Method not allowed'}, status=405)


def handler404(request, exception):
    return render(request, '404.html', status=404)

def admin_game_categories_api(request):
    """API for managing game categories"""
    if request.method == 'GET':
        # Get all categories with game counts
        categories = GameCategory.objects.annotate(game_count=Count('game')).all()
        categories_data = []
        for category in categories:
            categories_data.append({
                'id': category.id,
                'name': category.name,
                'emoji': category.emoji,
                'tag_class': category.tag_class,
                'game_count': category.game_count
            })
        return JsonResponse({'categories': categories_data})
    
    elif request.method == 'POST':
        # Add new category
        try:
            data = json.loads(request.body)
            category = GameCategory.objects.create(
                name=data['name'],
                emoji=data.get('emoji', '🎮'),
                tag_class=data.get('tag_class', 'adventure')
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Category added successfully!',
                'category': {
                    'id': category.id,
                    'name': category.name,
                    'emoji': category.emoji
                }
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=400)
    
    elif request.method == 'PUT':
        # Update category
        try:
            data = json.loads(request.body)
            category_id = data.get('id')
            category = GameCategory.objects.get(id=category_id)
            
            category.name = data.get('name', category.name)
            category.emoji = data.get('emoji', category.emoji)
            category.tag_class = data.get('tag_class', category.tag_class)
            category.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Category updated successfully!',
                'category': {
                    'id': category.id,
                    'name': category.name,
                    'emoji': category.emoji
                }
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=400)
    
    elif request.method == 'DELETE':
        # Delete category
        try:
            data = json.loads(request.body)
            category_id = data.get('id')
            category = GameCategory.objects.get(id=category_id)
            category.delete()
            
            return JsonResponse({
                'success': True,
                'message': 'Category deleted successfully!'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=400)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@csrf_exempt
def admin_packages_api(request):
    """API for managing packages"""
    if request.method == 'GET':
        # Get all packages
        packages = Package.objects.all().order_by('order', 'price')
        packages_data = []
        for package in packages:
            packages_data.append({
                'id': package.id,
                'name': package.name,
                'tagline': package.tagline,
                'price': float(package.price),
                'duration': package.duration,
                'features': package.features,
                'features_list': package.get_features_list(),
                'color_scheme': package.color_scheme,
                'is_featured': package.is_featured,
                'order': package.order,
                'is_active': package.is_active,
            })
        return JsonResponse({'packages': packages_data})
    
    elif request.method == 'POST':
        # Add new package
        try:
            data = json.loads(request.body)
            
            package = Package.objects.create(
                name=data['name'],
                tagline=data['tagline'],
                price=data['price'],
                duration=data['duration'],
                features=data['features'],
                color_scheme=data['color_scheme'],
                is_featured=data.get('is_featured', False),
                order=data.get('order', 0),
                is_active=data.get('is_active', True)
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Package added successfully!',
                'package': {
                    'id': package.id,
                    'name': package.name,
                    'price': float(package.price),
                    'duration': package.duration
                }
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=400)
    
    elif request.method == 'PUT':
        # Update existing package
        try:
            data = json.loads(request.body)
            package_id = data.get('id')
            package = Package.objects.get(id=package_id)
            
            package.name = data.get('name', package.name)
            package.tagline = data.get('tagline', package.tagline)
            package.price = data.get('price', package.price)
            package.duration = data.get('duration', package.duration)
            package.features = data.get('features', package.features)
            package.color_scheme = data.get('color_scheme', package.color_scheme)
            package.is_featured = data.get('is_featured', package.is_featured)
            package.order = data.get('order', package.order)
            package.is_active = data.get('is_active', package.is_active)
            
            package.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Package updated successfully!',
                'package': {
                    'id': package.id,
                    'name': package.name,
                    'price': float(package.price),
                    'duration': package.duration
                }
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=400)
    
    elif request.method == 'DELETE':
        # Delete package
        try:
            data = json.loads(request.body)
            package_id = data.get('id')
            package = Package.objects.get(id=package_id)
            package.delete()
            
            return JsonResponse({
                'success': True,
                'message': 'Package deleted successfully!'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=400)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


# Payment Gateway Views

@csrf_exempt
def create_payment_order(request):
    """Create Razorpay payment order for package purchase"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            package_id = data.get('package_id')
            customer_name = data.get('customer_name')
            customer_email = data.get('customer_email')
            customer_phone = data.get('customer_phone')
            
            # Validate package
            package = get_object_or_404(Package, id=package_id, is_active=True)
            
            # Create Razorpay order
            import razorpay
            client = razorpay.Client(
                auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
            )
            
            # Convert amount to paise (Razorpay uses paise)
            amount_paise = int(package.price * 100)
            
            razorpay_order = client.order.create({
                'amount': amount_paise,
                'currency': 'INR',
                'receipt': f'receipt_{package_id}_{uuid.uuid4().hex[:8]}',
                'payment_capture': 1
            })
            
            # Create payment record
            payment = Payment.objects.create(
                package=package,
                customer_name=customer_name,
                customer_email=customer_email,
                customer_phone=customer_phone,
                amount=package.price,
                razorpay_order_id=razorpay_order['id'],
                status='pending'
            )
            
            return JsonResponse({
                'success': True,
                'order_id': razorpay_order['id'],
                'amount': amount_paise,
                'currency': 'INR',
                'key_id': settings.RAZORPAY_KEY_ID,
                'payment_id': payment.id
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=400)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@csrf_exempt
def verify_payment(request):
    """Verify Razorpay payment and generate package card"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            razorpay_order_id = data.get('razorpay_order_id')
            razorpay_payment_id = data.get('razorpay_payment_id')
            razorpay_signature = data.get('razorpay_signature')
            payment_id = data.get('payment_id')
            
            # Get payment record
            payment = get_object_or_404(Payment, id=payment_id, razorpay_order_id=razorpay_order_id)
            
            # Verify signature
            import razorpay
            client = razorpay.Client(
                auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
            )
            
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            }
            
            try:
                client.utility.verify_payment_signature(params_dict)
            except razorpay.errors.SignatureVerificationError:
                return JsonResponse({
                    'success': False,
                    'message': 'Payment verification failed'
                }, status=400)
            
            # Update payment record
            payment.razorpay_payment_id = razorpay_payment_id
            payment.razorpay_signature = razorpay_signature
            payment.status = 'captured'
            payment.save()
            
            # Generate package card
            valid_until = timezone.now() + timedelta(days=365)  # Valid for 1 year
            package_card = PackageCard.objects.create(
                payment=payment,
                customer_name=payment.customer_name,
                package_name=payment.package.name,
                package_price=payment.amount,
                valid_until=valid_until
            )
            
            # Generate QR code
            try:
                package_card.generate_qr_code()
            except Exception as qr_error:
                print(f"QR code generation failed: {qr_error}")
            
            return JsonResponse({
                'success': True,
                'message': 'Payment successful! Package card generated.',
                'card_id': str(package_card.card_id),
                'customer_name': package_card.customer_name,
                'package_name': package_card.package_name,
                'valid_until': package_card.valid_until.strftime('%Y-%m-%d %H:%M')
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=400)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


def download_package_card(request, card_id):
    """Download package card as PDF"""
    try:
        package_card = get_object_or_404(PackageCard, card_id=card_id)
        
        if not package_card.is_valid():
            return JsonResponse({'error': 'Card is not valid or has been used'}, status=400)
        
        # Generate PDF card
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.lib.colors import Color, black, white
        from reportlab.lib.units import inch
        from io import BytesIO
        from django.http import HttpResponse
        
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        
        # Card background
        if package_card.payment.package.color_scheme == 'gold':
            bg_color = Color(0.83, 0.69, 0.22)  # Gold
        elif package_card.payment.package.color_scheme == 'silver':
            bg_color = Color(0.75, 0.75, 0.75)  # Silver
        else:
            bg_color = Color(0.72, 0.45, 0.20)  # Bronze
        
        # Draw card background
        p.setFillColor(bg_color)
        p.rect(50, height - 350, 500, 300, fill=True, stroke=True)
        
        # Add white inner rectangle
        p.setFillColor(white)
        p.rect(60, height - 340, 480, 280, fill=True)
        
        # Add title
        p.setFillColor(black)
        p.setFont("Helvetica-Bold", 24)
        p.drawString(200, height - 100, "HAPPY HOOPERS")
        
        p.setFont("Helvetica-Bold", 18)
        p.drawString(150, height - 130, f"{package_card.package_name.upper()} PACKAGE")
        
        # Add customer details
        p.setFont("Helvetica", 14)
        p.drawString(80, height - 180, f"Customer: {package_card.customer_name}")
        p.drawString(80, height - 210, f"Card ID: {package_card.card_id}")
        p.drawString(80, height - 240, f"Valid Until: {package_card.valid_until.strftime('%d-%m-%d %H:%M')}")
        
        # Add QR code if available
        if package_card.qr_code_url:
            try:
                from PIL import Image
                img_path = package_card.qr_code_url.path
                if os.path.exists(img_path):
                    img = Image.open(img_path)
                    img_width, img_height = img.size
                    aspect = img_width / img_height
                    qr_width = 100
                    qr_height = qr_width / aspect
                    p.drawImage(img_path, 420, height - 280, width=qr_width, height=qr_height)
            except Exception as e:
                print(f"Error adding QR code to PDF: {e}")
        
        # Add footer
        p.setFont("Helvetica-Oblique", 10)
        p.drawString(80, height - 320, "This card is property of Happy Hoopers Play Arena & Café")
        
        p.showPage()
        p.save()
        
        buffer.seek(0)
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="package_card_{card_id}.pdf"'
        
        return response
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def view_package_card(request, card_id):
    """View package card details"""
    try:
        package_card = get_object_or_404(PackageCard, card_id=card_id)
        
        return JsonResponse({
            'success': True,
            'card': {
                'card_id': str(package_card.card_id),
                'customer_name': package_card.customer_name,
                'package_name': package_card.package_name,
                'package_price': float(package_card.package_price),
                'valid_from': package_card.valid_from.strftime('%Y-%m-%d %H:%M'),
                'valid_until': package_card.valid_until.strftime('%Y-%m-%d %H:%M'),
                'is_used': package_card.is_used,
                'is_valid': package_card.is_valid(),
                'qr_code_url': package_card.qr_code_url.url if package_card.qr_code_url else None
            }
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def create_membership_order(request):
    """Create Razorpay order for membership purchase"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            duration = data.get('duration')
            customer_name = data.get('customer_name')
            customer_email = data.get('customer_email')
            customer_phone = data.get('customer_phone')
            
            # Validate duration
            if duration not in ['3_months', '6_months']:
                return JsonResponse({'success': False, 'message': 'Invalid duration selected'})
            
            # Calculate price based on duration
            if duration == '3_months':
                price = 2000
            elif duration == '6_months':
                price = 3000
            else:
                price = 0
            
            # Create Razorpay order
            import razorpay
            client = razorpay.Client(
                auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
            )
            
            # Convert amount to paise (Razorpay uses paise)
            amount_paise = int(price * 100)
            
            razorpay_order = client.order.create({
                'amount': amount_paise,
                'currency': 'INR',
                'receipt': f'membership_{duration}_{uuid.uuid4().hex[:8]}',
                'payment_capture': 1
            })
            
            # Create membership record
            membership = MembershipCard.objects.create(
                customer_name=customer_name,
                customer_email=customer_email,
                customer_phone=customer_phone,
                duration=duration,
                price=price,
                razorpay_order_id=razorpay_order['id'],
                status='active'
            )
            
            return JsonResponse({
                'success': True,
                'order_id': razorpay_order['id'],
                'membership_id': membership.id,
                'amount': amount_paise,
                'currency': 'INR',
                'key_id': settings.RAZORPAY_KEY_ID,
                'duration': duration,
                'price': price
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=500)
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=405)


@csrf_exempt
def verify_membership_payment(request):
    """Verify Razorpay payment for membership and generate card"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            razorpay_payment_id = data.get('razorpay_payment_id')
            razorpay_order_id = data.get('razorpay_order_id')
            razorpay_signature = data.get('razorpay_signature')
            membership_id = data.get('membership_id')
            
            # Get membership record
            try:
                membership = MembershipCard.objects.get(id=membership_id, razorpay_order_id=razorpay_order_id)
            except MembershipCard.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'Invalid membership record'}, status=400)
            
            # Verify payment signature
            import razorpay
            client = razorpay.Client(
                auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
            )
            
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            }
            
            try:
                client.utility.verify_payment_signature(params_dict)
            except razorpay.errors.SignatureVerificationError:
                return JsonResponse({'success': False, 'message': 'Payment verification failed'}, status=400)
            
            # Update membership record
            membership.razorpay_payment_id = razorpay_payment_id
            membership.razorpay_signature = razorpay_signature
            membership.status = 'active'
            membership.save()
            
            # Generate QR code and card
            try:
                membership.generate_qr_code()
                membership.generate_card_image()
                membership.save()
            except Exception as e:
                print(f"Error generating card: {e}")
            
            return JsonResponse({
                'success': True,
                'card_id': str(membership.card_id),
                'customer_name': membership.customer_name,
                'duration': membership.get_duration_display(),
                'valid_until': membership.valid_until.strftime('%Y-%m-%d %H:%M'),
                'discount_percentage': membership.discount_percentage
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=500)
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=405)


def download_membership_card(request, card_id):
    """Download membership card PDF"""
    try:
        membership = get_object_or_404(MembershipCard, card_id=card_id)
        
        if not membership.card_image:
            return HttpResponse("Card not generated yet", status=404)
        
        # Serve the file
        response = HttpResponse(membership.card_image.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="membership_card_{membership.card_id}.pdf"'
        return response
        
    except Exception as e:
        return HttpResponse(f"Error downloading card: {str(e)}", status=500)


def view_membership_card(request, card_id):
    """View membership card details"""
    try:
        membership = get_object_or_404(MembershipCard, card_id=card_id)
        
        return JsonResponse({
            'success': True,
            'card': {
                'card_id': str(membership.card_id),
                'customer_name': membership.customer_name,
                'duration': membership.get_duration_display(),
                'price': float(membership.price),
                'discount_percentage': membership.discount_percentage,
                'valid_from': membership.valid_from.strftime('%Y-%m-%d %H:%M'),
                'valid_until': membership.valid_until.strftime('%Y-%m-%d %H:%M'),
                'status': membership.status,
                'is_valid': membership.is_valid(),
                'qr_code_url': membership.qr_code_url.url if membership.qr_code_url else None
            }
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def membership(request):
    """Membership card purchase page"""
    context = {
        'site_settings': get_site_settings(),
    }
    return render(request, 'arena/membership.html', context)


def admin_membership_cards(request):
    """Admin view to see all membership cards"""
    if not request.user.is_staff:
        return redirect('admin:login')
    
    memberships = MembershipCard.objects.all().order_by('-created_at')
    
    context = {
        'memberships': memberships,
        'site_settings': get_site_settings(),
    }
    return render(request, 'arena/admin_membership_cards.html', context)


def test_payment_config(request):
    """Test payment configuration"""
    try:
        from django.conf import settings
        
        # Test Razorpay configuration
        import razorpay
        client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
        )
        
        # Test connection by fetching balance
        balance = client.balance.fetch()
        
        return JsonResponse({
            'success': True,
            'message': 'Razorpay configuration is working',
            'razorpay_key_id': settings.RAZORPAY_KEY_ID[:10] + '...',
            'balance': balance
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Razorpay configuration error: {str(e)}'
        }, status=500)
