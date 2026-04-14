from django.urls import path
from . import views

app_name = 'arena'

urlpatterns = [
    # Main pages
    path('', views.home, name='home'),
    path('games/', views.games, name='games'),
    path('packages/', views.packages, name='packages'),
    path('cafe/', views.cafe, name='cafe'),
    path('birthday/', views.birthday, name='birthday'),
    path('cricket-booking/', views.cricket_booking, name='cricket_booking'),
    path('gallery/', views.gallery, name='gallery'),
    path('contact/', views.contact, name='contact'),
    path('about/', views.about, name='about'),
    path('place-order/', views.place_order, name='place_order'),
    
    # AJAX endpoints
    path('add-to-cart/', views.add_to_cart, name='add_to_cart'),
    path('update-cart/', views.update_cart, name='update_cart'),
    path('clear-cart/', views.clear_cart, name='clear_cart'),
    
    # Admin panel
    path('admin-login/', views.admin_login, name='admin_login'),
    path('admin-logout/', views.admin_logout, name='admin_logout'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    
    # AJAX endpoints
    path('api/games/', views.api_games, name='api_games'),
    path('api/cafe-items/', views.api_cafe_items, name='api_cafe_items'),
    path('api/packages/', views.api_packages, name='api_packages'),
    path('api/testimonials/', views.api_testimonials, name='api_testimonials'),
    
    # Admin API endpoints
    path('api/admin/games/', views.admin_games_api, name='admin_games_api'),
    path('api/admin/game-categories/', views.admin_game_categories_api, name='admin_game_categories_api'),
    path('api/admin/packages/', views.admin_packages_api, name='admin_packages_api'),
    path('api/admin/cafe-items/', views.admin_cafe_items_api, name='admin_cafe_items_api'),
    path('api/admin/cafe-categories/', views.admin_cafe_categories_api, name='admin_cafe_categories_api'),
    path('api/admin/gallery/', views.admin_gallery_api, name='admin_gallery_api'),
    path('api/admin/cricket-bookings/', views.admin_cricket_bookings_api, name='admin_cricket_bookings_api'),
    path('api/admin/cricket-pricing/', views.admin_cricket_pricing_api, name='admin_cricket_pricing_api'),
    path('api/admin/cafe-orders/', views.admin_cafe_orders_api, name='admin_cafe_orders_api'),
    path('api/admin/inquiries/', views.admin_inquiries_api, name='admin_inquiries_api'),
    path('api/admin/contact-info/', views.admin_contact_info_api, name='admin_contact_info_api'),
    
    # Form submissions
    path('check-cricket-availability/', views.check_cricket_availability, name='check_cricket_availability'),
    path('update-cafe-stock/', views.update_cafe_stock, name='update_cafe_stock'),
    
    # Payment Gateway
    path('payment/create-order/', views.create_payment_order, name='create_payment_order'),
    path('payment/verify/', views.verify_payment, name='verify_payment'),
    path('payment/test-config/', views.test_payment_config, name='test_payment_config'),
    path('card/<uuid:card_id>/download/', views.download_package_card, name='download_package_card'),
    path('card/<uuid:card_id>/view/', views.view_package_card, name='view_package_card'),
    
    # Membership Cards
    path('membership/', views.membership, name='membership'),
    path('membership/create-order/', views.create_membership_order, name='create_membership_order'),
    path('membership/verify/', views.verify_membership_payment, name='verify_membership_payment'),
    path('membership-card/<uuid:card_id>/download/', views.download_membership_card, name='download_membership_card'),
    path('membership-card/<uuid:card_id>/view/', views.view_membership_card, name='view_membership_card'),
    path('admin/membership-cards/', views.admin_membership_cards, name='admin_membership_cards'),
]
