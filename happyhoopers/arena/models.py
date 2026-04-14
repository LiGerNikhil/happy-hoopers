from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid
from datetime import timedelta

class AdminUser(models.Model):
    """Custom admin user model for authentication"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_super_admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Admin User"
        verbose_name_plural = "Admin Users"
    
    def __str__(self):
        return self.user.username
    
    @property
    def is_admin(self):
        """Check if user has admin privileges"""
        return True


class GameCategory(models.Model):
    name = models.CharField(max_length=50, unique=True)
    emoji = models.CharField(max_length=10, default='🎮')
    tag_class = models.CharField(max_length=20, default='adventure')
    
    def __str__(self):
        return self.name


class Game(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(GameCategory, on_delete=models.CASCADE)
    description = models.TextField()
    duration = models.CharField(max_length=50)  # e.g., "30 min", "Unlimited"
    age_group = models.CharField(max_length=20)  # e.g., "5–13", "2–8"
    price_info = models.CharField(max_length=100)  # e.g., "Incl. Gold", "₹100/15 min"
    package = models.CharField(max_length=50, choices=[
        ('bronze', 'Bronze Package'),
        ('silver', 'Silver Package'),
        ('gold', 'Gold Package'),
        ('individual', 'Individual'),
    ])
    image_url = models.URLField(max_length=500, blank=True, null=True)
    is_popular = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name


class CafeCategory(models.Model):
    name = models.CharField(max_length=50, unique=True)
    emoji = models.CharField(max_length=10, default='🍽️')
    tag_class = models.CharField(max_length=20, default='cp-bev')
    
    def __str__(self):
        return self.name


class CafeItem(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(CafeCategory, on_delete=models.CASCADE)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.PositiveIntegerField(default=0)
    image_url = models.URLField(max_length=500, blank=True, null=True)
    image = models.ImageField(upload_to='cafe/', blank=True, null=True)
    is_available = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order', 'name']
    
    def __str__(self):
        return f"{self.name} - ₹{self.price}"
    
    @property
    def is_low_stock(self):
        return self.stock_quantity <= 10


class Package(models.Model):
    name = models.CharField(max_length=50)
    tagline = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.CharField(max_length=50)  # e.g., "2 hours", "Full day"
    features = models.TextField(help_text="Enter features separated by new lines")
    color_scheme = models.CharField(max_length=20, choices=[
        ('bronze', 'Bronze'),
        ('silver', 'Silver'),
        ('gold', 'Gold'),
    ])
    is_featured = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['order', 'price']
    
    def __str__(self):
        return f"{self.name} - ₹{self.price}"
    
    def get_features_list(self):
        """Convert features text to list"""
        if self.features:
            return [feature.strip() for feature in self.features.split('\n') if feature.strip()]
        return []


class CricketPricing(models.Model):
    """Cricket slot pricing configuration"""
    name = models.CharField(max_length=50)  # e.g., "Morning", "Evening", "Weekend"
    start_time = models.TimeField()
    end_time = models.TimeField()
    price_per_slot = models.DecimalField(max_digits=6, decimal_places=2, help_text="Price per 15 minutes")
    days_applicable = models.CharField(max_length=50, help_text="e.g., 'Mon-Fri', 'Sat-Sun', 'All'")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Cricket Pricing"
        verbose_name_plural = "Cricket Pricing"
        ordering = ['start_time']
    
    def __str__(self):
        return f"{self.name} ({self.start_time}-{self.end_time}) - ₹{self.price_per_slot}"


class CricketBooking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]
    
    booking_id = models.CharField(max_length=20, unique=True, editable=False)
    name = models.CharField(max_length=100)
    mobile = models.CharField(max_length=15)
    email = models.EmailField(blank=True, null=True)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    duration_minutes = models.PositiveIntegerField()
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.booking_id} - {self.name} - {self.date}"
    
    def save(self, *args, **kwargs):
        if not self.booking_id:
            self.booking_id = f"HH{str(uuid.uuid4())[:8].upper()}"
        
        # Calculate duration and cost if not provided
        if self.start_time and self.end_time and not self.duration_minutes:
            start_minutes = self.start_time.hour * 60 + self.start_time.minute
            end_minutes = self.end_time.hour * 60 + self.end_time.minute
            self.duration_minutes = end_minutes - start_minutes
        
        if self.duration_minutes and not self.cost:
            # Calculate cost based on pricing
            cost = self.calculate_cost()
            self.cost = cost
        
        super().save(*args, **kwargs)
    
    def calculate_cost(self):
        """Calculate booking cost based on duration and pricing"""
        if not self.duration_minutes:
            return 0
        
        # Get applicable pricing for day and time
        day_of_week = self.date.strftime('%A')
        time = self.start_time
        
        applicable_pricing = CricketPricing.objects.filter(
            is_active=True,
            start_time__lte=time,
            end_time__gte=time
        ).first()
        
        if applicable_pricing:
            # Check if pricing applies to this day
            days = applicable_pricing.days_applicable
            if days == 'All' or day_of_week[:3] in days:
                # Calculate number of 15-minute slots
                slots = (self.duration_minutes + 14) // 15  # Round up
                return slots * applicable_pricing.price_per_slot
        
        # Default pricing: ₹100 per 15 minutes
        slots = (self.duration_minutes + 14) // 15
        return slots * 100
    
    def check_conflict(self):
        """Check if this booking conflicts with existing bookings"""
        conflicting_bookings = CricketBooking.objects.filter(
            date=self.date,
            status='confirmed',
            start_time__lt=self.end_time,
            end_time__gt=self.start_time
        ).exclude(id=self.id)
        
        return conflicting_bookings.exists()


class BirthdayParty(models.Model):
    STATUS_CHOICES = [
        ('inquiry', 'Inquiry'),
        ('booked', 'Booked'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]
    
    party_id = models.CharField(max_length=20, unique=True, editable=False)
    parent_name = models.CharField(max_length=100)
    child_name = models.CharField(max_length=100)
    child_age = models.PositiveIntegerField()
    mobile = models.CharField(max_length=15)
    email = models.EmailField(blank=True, null=True)
    party_date = models.DateField()
    party_time = models.TimeField()
    guest_count = models.PositiveIntegerField()
    theme = models.CharField(max_length=100, blank=True, null=True)
    package_chosen = models.ForeignKey(Package, on_delete=models.SET_NULL, null=True, blank=True)
    special_requirements = models.TextField(blank=True, null=True)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)
    advance_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='inquiry')
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-party_date', '-created_at']
    
    def __str__(self):
        return f"{self.party_id} - {self.child_name}'s Birthday"
    
    def save(self, *args, **kwargs):
        if not self.party_id:
            self.party_id = f"BD{str(uuid.uuid4())[:8].upper()}"
        super().save(*args, **kwargs)
    
    @property
    def balance_amount(self):
        return self.total_cost - self.advance_paid


class Testimonial(models.Model):
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=100)  # e.g., "Mom of 2", "Dad · Gold Package"
    rating = models.PositiveIntegerField(choices=[(i, f"{i} stars") for i in range(1, 6)])
    review_text = models.TextField()
    avatar_emoji = models.CharField(max_length=10, default='👤')
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order', '-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.rating} stars"


class ContactInquiry(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    mobile = models.CharField(max_length=15)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    is_resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.subject}"


class CafeOrder(models.Model):
    """Cafe order model for customer orders"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('preparing', 'Preparing'),
        ('ready', 'Ready'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    order_id = models.CharField(max_length=20, unique=True, editable=False)
    customer_name = models.CharField(max_length=100)
    mobile = models.CharField(max_length=15)
    table_number = models.CharField(max_length=10)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.order_id} - {self.customer_name} - Table {self.table_number}"
    
    def save(self, *args, **kwargs):
        if not self.order_id:
            self.order_id = f"CF{str(uuid.uuid4())[:8].upper()}"
        super().save(*args, **kwargs)


class CafeOrderItem(models.Model):
    """Individual items in a cafe order"""
    order = models.ForeignKey(CafeOrder, on_delete=models.CASCADE, related_name='items')
    cafe_item = models.ForeignKey(CafeItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price_per_item = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        ordering = ['order', 'id']
    
    def __str__(self):
        return f"{self.quantity}x {self.cafe_item.name} - Order {self.order.order_id}"
    
    def save(self, *args, **kwargs):
        # Calculate subtotal
        self.subtotal = self.quantity * self.price_per_item
        super().save(*args, **kwargs)


class SiteSettings(models.Model):
    key = models.CharField(max_length=100, unique=True)
    value = models.TextField()
    description = models.TextField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['key']
        verbose_name = "Site Setting"
        verbose_name_plural = "Site Settings"
    
    def __str__(self):
        return f"{self.key}: {self.value}"


class ContactInfo(models.Model):
    """Model for managing contact information that can be updated by Django admin"""
    phone = models.CharField(max_length=20, help_text="Main contact phone number")
    email = models.EmailField(help_text="Main contact email")
    address = models.TextField(help_text="Physical address")
    whatsapp = models.CharField(max_length=20, blank=True, null=True, help_text="WhatsApp number")
    facebook = models.URLField(blank=True, null=True, help_text="Facebook page URL")
    instagram = models.URLField(blank=True, null=True, help_text="Instagram profile URL")
    youtube = models.URLField(blank=True, null=True, help_text="YouTube channel URL")
    google_maps_url = models.URLField(blank=True, null=True, help_text="Google Maps location URL")
    working_hours = models.CharField(max_length=200, default="10AM - 10PM Daily", help_text="Business working hours")
    emergency_contact = models.CharField(max_length=20, blank=True, null=True, help_text="Emergency contact number")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Contact Information"
        verbose_name_plural = "Contact Information"
    
    def __str__(self):
        return f"Contact Info - {self.phone}"
    
    @classmethod
    def get_contact_info(cls):
        """Get the first contact info instance or create default"""
        contact_info, created = cls.objects.get_or_create(
            pk=1,
            defaults={
                'phone': '+91 98765 43210',
                'email': 'info@happyhoopers.com',
                'address': 'Gannavaram, Vijayawada, Andhra Pradesh 521102',
                'whatsapp': '+91 98765 43210',
                'working_hours': '10AM - 10PM Daily',
            }
        )
        return contact_info


class GalleryImage(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    image_url = models.URLField(max_length=500, blank=True, null=True)
    image = models.ImageField(upload_to='gallery/', blank=True, null=True)
    category = models.CharField(max_length=50, choices=[
        ('games', 'Games'),
        ('cafe', 'Café'),
        ('birthday', 'Birthday Parties'),
        ('facility', 'Facility'),
    ])
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order', '-created_at']
    
    def __str__(self):
        return self.title


class Payment(models.Model):
    """Payment model for Razorpay transactions"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('captured', 'Captured'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    package = models.ForeignKey(Package, on_delete=models.CASCADE)
    customer_name = models.CharField(max_length=100)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=15)
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # in INR
    razorpay_order_id = models.CharField(max_length=100, unique=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Payment {self.razorpay_order_id} - {self.status}"


class MembershipCard(models.Model):
    """Membership card for users with discount benefits"""
    DURATION_CHOICES = [
        ('3_months', '3 Months'),
        ('6_months', '6 Months'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
    ]
    
    customer_name = models.CharField(max_length=100)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=15)
    duration = models.CharField(max_length=20, choices=DURATION_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # in INR
    discount_percentage = models.IntegerField(default=10)  # 10% discount
    razorpay_order_id = models.CharField(max_length=100, unique=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    card_id = models.UUIDField(default=uuid.uuid4, unique=True)
    valid_from = models.DateTimeField(auto_now_add=True)
    valid_until = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    qr_code_url = models.URLField(max_length=500, blank=True, null=True)
    card_image = models.ImageField(upload_to='membership_cards/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'arena_membership_cards'
        verbose_name = 'Membership Card'
        verbose_name_plural = 'Membership Cards'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.customer_name} - {self.get_duration_display()} ({self.card_id})"
    
    def save(self, *args, **kwargs):
        # Set valid_until based on duration
        if not self.valid_until and self.duration:
            if self.duration == '3_months':
                self.valid_until = timezone.now() + timedelta(days=90)
            elif self.duration == '6_months':
                self.valid_until = timezone.now() + timedelta(days=180)
        
        # Set price based on duration
        if not self.price and self.duration:
            if self.duration == '3_months':
                self.price = 2000
            elif self.duration == '6_months':
                self.price = 3000
        
        super().save(*args, **kwargs)
    
    def is_valid(self):
        """Check if membership card is still valid"""
        return (
            self.status == 'active' and 
            self.valid_until and 
            timezone.now() <= self.valid_until
        )
    
    def generate_qr_code(self):
        """Generate QR code for the membership card"""
        import qrcode
        from io import BytesIO
        from django.core.files import File
        
        # Create QR code data
        qr_data = f"""
        HAPPY HOOPERS MEMBERSHIP CARD
        Card ID: {self.card_id}
        Name: {self.customer_name}
        Duration: {self.get_duration_display()}
        Valid Until: {self.valid_until.strftime('%Y-%m-%d')}
        Discount: {self.discount_percentage}%
        """
        
        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Save QR code
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        filename = f'membership_qr_{self.card_id}.png'
        
        self.qr_code_url.save(filename, File(buffer), save=False)
        buffer.close()
        
        return self.qr_code_url
    
    def generate_card_image(self):
        """Generate a visual membership card"""
        from reportlab.lib.pagesizes import credit_card_size
        from reportlab.lib.colors import Color, white, black
        from reportlab.lib.units import inch
        from reportlab.pdfgen import canvas
        from io import BytesIO
        from django.core.files import File
        
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=credit_card_size)
        width, height = credit_card_size
        
        # Card background gradient
        p.setFillColorRGB(0.2, 0.4, 0.8)  # Blue background
        p.rect(0, 0, width, height, fill=True, stroke=False)
        
        # Add white overlay for text area
        p.setFillColor(white)
        p.rect(20, height-80, width-40, 60, fill=True, stroke=False)
        
        # Title
        p.setFillColor(black)
        p.setFont("Helvetica-Bold", 16)
        p.drawString(30, height-50, "HAPPY HOOPERS")
        
        # Membership type
        p.setFont("Helvetica", 12)
        p.drawString(30, height-30, "MEMBERSHIP CARD")
        
        # Card ID
        p.setFont("Helvetica", 10)
        p.drawString(30, height-100, f"Card ID: {self.card_id}")
        
        # Customer info
        p.setFont("Helvetica-Bold", 12)
        p.drawString(30, height-130, self.customer_name)
        
        p.setFont("Helvetica", 10)
        p.drawString(30, height-150, f"Duration: {self.get_duration_display()}")
        p.drawString(30, height-170, f"Valid Until: {self.valid_until.strftime('%Y-%m-%d')}")
        p.drawString(30, height-190, f"Discount: {self.discount_percentage}% OFF")
        
        # Add QR code if exists
        if self.qr_code_url:
            try:
                from reportlab.lib.utils import ImageReader
                img_reader = ImageReader(self.qr_code_url.path)
                p.drawImage(img_reader, width-80, 20, 60, 60)
            except:
                pass
        
        p.save()
        
        filename = f'membership_card_{self.card_id}.pdf'
        self.card_image.save(filename, File(buffer), save=False)
        buffer.close()
        
        return self.card_image


class PackageCard(models.Model):
    """Generated card for successful package purchases"""
    payment = models.OneToOneField(Payment, on_delete=models.CASCADE)
    card_id = models.UUIDField(default=uuid.uuid4, unique=True)
    customer_name = models.CharField(max_length=100)
    package_name = models.CharField(max_length=50)
    package_price = models.DecimalField(max_digits=10, decimal_places=2)
    valid_from = models.DateTimeField(auto_now_add=True)
    valid_until = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    qr_code_url = models.URLField(max_length=500, blank=True, null=True)
    card_image = models.ImageField(upload_to='package_cards/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Card {self.card_id} - {self.customer_name}"
    
    def is_valid(self):
        """Check if card is still valid"""
        from django.utils import timezone
        return not self.is_used and timezone.now() <= self.valid_until
    
    def generate_qr_code(self):
        """Generate QR code for the card"""
        import qrcode
        from io import BytesIO
        from django.core.files.base import ContentFile
        
        # Create QR code data
        qr_data = f"CARD_ID:{self.card_id}\nCUSTOMER:{self.customer_name}\nPACKAGE:{self.package_name}\nVALID_UNTIL:{self.valid_until.strftime('%Y-%m-%d %H:%M')}"
        
        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        # Create image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Save to BytesIO
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        # Save to model
        self.qr_code_url.save(f'qr_{self.card_id}.png', ContentFile(buffer.read()), save=False)
        self.save()
