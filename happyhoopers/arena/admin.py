from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count
from .models import (
    GameCategory, Game, CafeCategory, CafeItem, Package,
    CricketBooking, BirthdayParty, Testimonial, ContactInquiry,
    GalleryImage, SiteSettings, Payment, PackageCard, MembershipCard
)


@admin.register(GameCategory)
class GameCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'emoji', 'tag_class', 'game_count']
    search_fields = ['name']
    
    def game_count(self, obj):
        return obj.game_set.count()
    game_count.short_description = 'Games'


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'package', 'duration', 'age_group', 'price_info', 'is_popular', 'is_active', 'order']
    list_filter = ['category', 'package', 'is_popular', 'is_active']
    search_fields = ['name', 'description']
    list_editable = ['is_popular', 'is_active', 'order']
    ordering = ['order', 'name']
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('name', 'category', 'description', 'order')
        }),
        ('Details', {
            'fields': ('duration', 'age_group', 'price_info', 'package')
        }),
        ('Media', {
            'fields': ('image_url',)
        }),
        ('Settings', {
            'fields': ('is_popular', 'is_active')
        }),
    )


@admin.register(CafeCategory)
class CafeCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'emoji', 'tag_class']
    search_fields = ['name']


@admin.register(CafeItem)
class CafeItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'stock_quantity', 'is_low_stock', 'is_available', 'order']
    list_filter = ['category', 'is_available']
    search_fields = ['name', 'description']
    list_editable = ['stock_quantity', 'is_available', 'order']
    ordering = ['order', 'name']
    
    def is_low_stock(self, obj):
        if obj.stock_quantity <= 10:
            return format_html('<span style="color: red; font-weight: bold;">⚠️ Low ({})</span>', obj.stock_quantity)
        return format_html('<span style="color: green;">✓ OK ({})</span>', obj.stock_quantity)
    is_low_stock.short_description = 'Stock Status'
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('name', 'category', 'description', 'order')
        }),
        ('Pricing', {
            'fields': ('price', 'stock_quantity')
        }),
        ('Media', {
            'fields': ('image_url',)
        }),
        ('Settings', {
            'fields': ('is_available',)
        }),
    )


@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'duration', 'color_scheme', 'is_featured', 'is_active', 'order']
    list_filter = ['color_scheme', 'is_featured', 'is_active']
    search_fields = ['name', 'tagline']
    list_editable = ['is_featured', 'is_active', 'order']
    ordering = ['order', 'price']
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('name', 'tagline', 'order')
        }),
        ('Pricing', {
            'fields': ('price', 'duration')
        }),
        ('Features', {
            'fields': ('features',)
        }),
        ('Settings', {
            'fields': ('color_scheme', 'is_featured', 'is_active')
        }),
    )


@admin.register(CricketBooking)
class CricketBookingAdmin(admin.ModelAdmin):
    list_display = ['booking_id', 'name', 'mobile', 'date', 'start_time', 'end_time', 'duration_minutes', 'cost', 'status']
    list_filter = ['status', 'date']
    search_fields = ['name', 'mobile', 'booking_id']
    readonly_fields = ['booking_id', 'created_at', 'updated_at']
    ordering = ['-date', '-created_at']
    
    fieldsets = (
        ('Booking Info', {
            'fields': ('booking_id', 'name', 'mobile', 'email')
        }),
        ('Schedule', {
            'fields': ('date', 'start_time', 'end_time', 'duration_minutes')
        }),
        ('Pricing', {
            'fields': ('cost', 'status')
        }),
        ('Additional', {
            'fields': ('notes',)
        }),
        ('System', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing existing object
            return self.readonly_fields + ['duration_minutes', 'cost']
        return self.readonly_fields


@admin.register(BirthdayParty)
class BirthdayPartyAdmin(admin.ModelAdmin):
    list_display = ['party_id', 'child_name', 'parent_name', 'mobile', 'party_date', 'guest_count', 'total_cost', 'balance_amount', 'status']
    list_filter = ['status', 'party_date']
    search_fields = ['child_name', 'parent_name', 'mobile', 'party_id']
    readonly_fields = ['party_id', 'created_at', 'updated_at', 'balance_amount']
    ordering = ['-party_date', '-created_at']
    
    fieldsets = (
        ('Party Info', {
            'fields': ('party_id', 'parent_name', 'child_name', 'child_age', 'mobile', 'email')
        }),
        ('Event Details', {
            'fields': ('party_date', 'party_time', 'guest_count', 'theme', 'package_chosen')
        }),
        ('Pricing', {
            'fields': ('total_cost', 'advance_paid', 'balance_amount')
        }),
        ('Additional', {
            'fields': ('special_requirements', 'notes', 'status')
        }),
        ('System', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ['name', 'role', 'rating_display', 'is_active', 'order']
    list_filter = ['rating', 'is_active']
    search_fields = ['name', 'role', 'review_text']
    list_editable = ['is_active', 'order']
    ordering = ['order', '-created_at']
    
    def rating_display(self, obj):
        return format_html('⭐' * obj.rating)
    rating_display.short_description = 'Rating'
    
    fieldsets = (
        ('Testimonial', {
            'fields': ('name', 'role', 'rating', 'review_text')
        }),
        ('Display', {
            'fields': ('avatar_emoji', 'is_active', 'order')
        }),
    )


@admin.register(ContactInquiry)
class ContactInquiryAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'mobile', 'subject', 'is_resolved', 'created_at']
    list_filter = ['is_resolved', 'created_at']
    search_fields = ['name', 'email', 'subject', 'message']
    list_editable = ['is_resolved']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Contact Info', {
            'fields': ('name', 'email', 'mobile')
        }),
        ('Inquiry', {
            'fields': ('subject', 'message')
        }),
        ('Status', {
            'fields': ('is_resolved',)
        }),
    )


@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'is_active', 'order', 'created_at']
    list_filter = ['category', 'is_active']
    search_fields = ['title', 'description']
    list_editable = ['is_active', 'order']
    ordering = ['order', '-created_at']
    
    fieldsets = (
        ('Image Info', {
            'fields': ('title', 'description', 'category', 'order')
        }),
        ('Media', {
            'fields': ('image_url',)
        }),
        ('Settings', {
            'fields': ('is_active',)
        }),
    )


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ['key', 'value_preview', 'description', 'updated_at']
    search_fields = ['key', 'description']
    ordering = ['key']
    
    def value_preview(self, obj):
        preview = obj.value[:50]
        if len(obj.value) > 50:
            preview += '...'
        return preview
    value_preview.short_description = 'Value'
    
    fieldsets = (
        ('Setting', {
            'fields': ('key', 'description')
        }),
        ('Content', {
            'fields': ('value',)
        }),
    )


# Custom admin site title
admin.site.site_header = 'Happy Hoopers Admin'
admin.site.site_title = 'Happy Hoopers'
admin.site.index_title = 'Welcome to Happy Hoopers Administration'


# Payment and Card Models
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('razorpay_order_id', 'customer_name', 'customer_email', 'package', 'amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('customer_name', 'customer_email', 'razorpay_order_id', 'razorpay_payment_id')
    readonly_fields = ('razorpay_order_id', 'razorpay_payment_id', 'razorpay_signature', 'created_at', 'updated_at')
    ordering = ('-created_at',)


@admin.register(PackageCard)
class PackageCardAdmin(admin.ModelAdmin):
    list_display = ('card_id', 'payment', 'customer_name', 'package_name', 'valid_until', 'is_used', 'created_at')
    list_filter = ('is_used', 'created_at', 'valid_until')
    search_fields = ('card_id', 'customer_name', 'package_name')
    readonly_fields = ('card_id', 'payment', 'customer_name', 'package_name', 'package_price', 'valid_from', 'valid_until', 'created_at')
    ordering = ('-created_at',)


@admin.register(MembershipCard)
class MembershipCardAdmin(admin.ModelAdmin):
    list_display = ('card_id', 'customer_name', 'customer_email', 'duration', 'price', 'status', 'valid_until', 'created_at')
    list_filter = ('duration', 'status', 'created_at', 'valid_until')
    search_fields = ('customer_name', 'customer_email', 'card_id', 'razorpay_order_id', 'razorpay_payment_id')
    readonly_fields = ('card_id', 'razorpay_order_id', 'razorpay_payment_id', 'razorpay_signature', 'valid_from', 'valid_until', 'created_at', 'updated_at')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Customer Information', {
            'fields': ('customer_name', 'customer_email', 'customer_phone')
        }),
        ('Membership Details', {
            'fields': ('duration', 'price', 'discount_percentage', 'status')
        }),
        ('Payment Information', {
            'fields': ('razorpay_order_id', 'razorpay_payment_id', 'razorpay_signature')
        }),
        ('Card Details', {
            'fields': ('card_id', 'valid_from', 'valid_until', 'card_image')
        }),
        ('System Information', {
            'fields': ('is_used', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(self.readonly_fields)
        if obj:  # Editing existing object
            readonly_fields.extend(['duration', 'price'])  # Don't allow editing duration/price after creation
        return readonly_fields
