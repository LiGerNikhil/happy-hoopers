from django import forms
from django.core.validators import RegexValidator
from django.utils import timezone
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from .models import CricketBooking, BirthdayParty, ContactInquiry, CricketPricing, CafeOrder, Package, ContactInfo


class ContactInfoForm(forms.ModelForm):
    """Form for managing contact information"""
    class Meta:
        model = ContactInfo
        fields = ['phone', 'email', 'address', 'whatsapp', 'facebook', 'instagram', 'youtube', 'google_maps_url', 'working_hours', 'emergency_contact']
        widgets = {
            'phone': forms.TextInput(attrs={'placeholder': '+91 98765 43210'}),
            'email': forms.EmailInput(attrs={'placeholder': 'info@happyhoopers.com'}),
            'address': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Gannavaram, Vijayawada, Andhra Pradesh 521102'}),
            'whatsapp': forms.TextInput(attrs={'placeholder': '+91 98765 43210'}),
            'facebook': forms.URLInput(attrs={'placeholder': 'https://facebook.com/happyhoopers'}),
            'instagram': forms.URLInput(attrs={'placeholder': 'https://instagram.com/happyhoopers'}),
            'youtube': forms.URLInput(attrs={'placeholder': 'https://youtube.com/@happyhoopers'}),
            'google_maps_url': forms.URLInput(attrs={'placeholder': 'https://maps.google.com/...'}),
            'working_hours': forms.TextInput(attrs={'placeholder': '10AM - 10PM Daily'}),
            'emergency_contact': forms.TextInput(attrs={'placeholder': '+91 98765 43210'}),
        }
        help_texts = {
            'phone': 'Main contact phone number displayed on website',
            'email': 'Main contact email for inquiries and bookings',
            'address': 'Physical address of the play arena',
            'whatsapp': 'WhatsApp number for quick contact',
            'facebook': 'Facebook page URL for social media link',
            'instagram': 'Instagram profile URL for social media link',
            'youtube': 'YouTube channel URL for video content',
            'google_maps_url': 'Google Maps URL for location directions',
            'working_hours': 'Business operating hours',
            'emergency_contact': 'Emergency contact number if different from main phone',
        }


class PackageForm(forms.ModelForm):
    class Meta:
        model = Package
        fields = ['name', 'tagline', 'price', 'duration', 'features', 'color_scheme', 'is_featured', 'order', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'e.g., Bronze Package'}),
            'tagline': forms.TextInput(attrs={'placeholder': 'e.g., Perfect for small groups'}),
            'price': forms.NumberInput(attrs={'placeholder': '299', 'step': '0.01'}),
            'duration': forms.TextInput(attrs={'placeholder': 'e.g., 2 hours, Full day'}),
            'features': forms.Textarea(attrs={'rows': 6, 'placeholder': 'Enter each feature on a new line:\nAccess to basic games\nBuilding blocks area\nParty decorations\n'}),
            'color_scheme': forms.Select(choices=[
                ('bronze', 'Bronze'),
                ('silver', 'Silver'),
                ('gold', 'Gold'),
            ]),
            'order': forms.NumberInput(attrs={'placeholder': '0'}),
        }
        help_texts = {
            'features': 'Enter each feature on a new line. These will be displayed as bullet points.',
            'order': 'Lower numbers appear first. Use to control package display order.',
            'is_featured': 'Featured packages are highlighted on the website.',
        }


class CafeOrderForm(forms.ModelForm):
    mobile = forms.CharField(
        max_length=15,
        validators=[RegexValidator(r'^\d{10}$', 'Enter a valid 10-digit mobile number')]
    )
    
    class Meta:
        model = CafeOrder
        fields = ['customer_name', 'mobile', 'table_number', 'notes']
        widgets = {
            'customer_name': forms.TextInput(attrs={'placeholder': 'Enter your name'}),
            'table_number': forms.TextInput(attrs={'placeholder': 'e.g., T1, T2, etc.'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Any special requests?'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['mobile'].widget.attrs.update({'placeholder': '10-digit mobile number'})


class CricketBookingForm(forms.ModelForm):
    mobile = forms.CharField(
        max_length=15,
        validators=[RegexValidator(r'^\d{10}$', 'Enter a valid 10-digit mobile number')]
    )
    
    class Meta:
        model = CricketBooking
        fields = ['name', 'mobile', 'email', 'date', 'start_time', 'end_time', 'notes']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'min': timezone.now().date()}),
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'placeholder': 'Enter your full name'})
        self.fields['mobile'].widget.attrs.update({'placeholder': '10-digit mobile number'})
        self.fields['email'].widget.attrs.update({'placeholder': 'email@example.com'})
        self.fields['notes'].widget.attrs.update({'placeholder': 'Any special requirements?'})
    
    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        date = cleaned_data.get('date')
        
        if start_time and end_time:
            if end_time <= start_time:
                raise forms.ValidationError("End time must be after start time")
            
            # Calculate duration in minutes
            start_minutes = start_time.hour * 60 + start_time.minute
            end_minutes = end_time.hour * 60 + end_time.minute
            duration = end_minutes - start_minutes
            
            if duration < 15:
                raise forms.ValidationError("Minimum booking duration is 15 minutes")
            
            if duration > 240:  # 4 hours max
                raise forms.ValidationError("Maximum booking duration is 4 hours")
            
            cleaned_data['duration_minutes'] = duration
            
            # Check for conflicts
            if date:
                # Create a temporary booking instance to check conflicts
                temp_booking = CricketBooking(
                    date=date,
                    start_time=start_time,
                    end_time=end_time
                )
                if temp_booking.check_conflict():
                    raise forms.ValidationError("This time slot is already booked. Please choose a different time.")
        
        return cleaned_data
    
    def get_cost_estimate(self):
        """Get cost estimate for current form data"""
        if not self.is_valid():
            return 0
        
        duration = self.cleaned_data.get('duration_minutes', 0)
        if not duration:
            return 0
        
        # Calculate slots and cost
        slots = (duration + 14) // 15  # Round up to nearest 15 minutes
        
        # Get pricing for the selected time
        date = self.cleaned_data.get('date')
        start_time = self.cleaned_data.get('start_time')
        
        if date and start_time:
            day_of_week = date.strftime('%A')
            applicable_pricing = CricketPricing.objects.filter(
                is_active=True,
                start_time__lte=start_time,
                end_time__gte=start_time
            ).first()
            
            if applicable_pricing:
                days = applicable_pricing.days_applicable
                if days == 'All' or day_of_week[:3] in days:
                    return slots * applicable_pricing.price_per_slot
        
        return slots * 100  # Default pricing


class CricketPricingForm(forms.ModelForm):
    class Meta:
        model = CricketPricing
        fields = ['name', 'start_time', 'end_time', 'price_per_slot', 'days_applicable', 'is_active']
        widgets = {
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
            'days_applicable': forms.Select(choices=[
                ('All', 'All Days'),
                ('Mon-Fri', 'Monday to Friday'),
                ('Sat-Sun', 'Saturday & Sunday'),
                ('Mon-Sat', 'Monday to Saturday'),
                ('Sun', 'Sunday Only'),
            ]),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        
        if start_time and end_time and end_time <= start_time:
            raise forms.ValidationError("End time must be after start time")
        
        return cleaned_data


class AdminLoginForm(AuthenticationForm):
    """Custom login form for admin dashboard"""
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your username',
            'autofocus': True
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password'
        })
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = "Username"
        self.fields['password'].label = "Password"


class CricketBookingForm(forms.ModelForm):
    mobile = forms.CharField(
        max_length=15,
        validators=[RegexValidator(r'^\d{10}$', 'Enter a valid 10-digit mobile number')]
    )
    
    class Meta:
        model = CricketBooking
        fields = ['name', 'mobile', 'email', 'date', 'start_time', 'end_time', 'notes']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'min': timezone.now().date()}),
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'placeholder': 'Enter your full name'})
        self.fields['mobile'].widget.attrs.update({'placeholder': '10-digit mobile number'})
        self.fields['email'].widget.attrs.update({'placeholder': 'email@example.com'})
        self.fields['notes'].widget.attrs.update({'placeholder': 'Any special requirements?'})
    
    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        
        if start_time and end_time:
            if end_time <= start_time:
                raise forms.ValidationError("End time must be after start time")
            
            # Calculate duration in minutes
            start_minutes = start_time.hour * 60 + start_time.minute
            end_minutes = end_time.hour * 60 + end_time.minute
            duration = end_minutes - start_minutes
            
            cleaned_data['duration_minutes'] = duration
            # Calculate cost (₹100 per 15 minutes)
            slots = (duration + 14) // 15  # Round up to nearest 15 minutes
            cleaned_data['cost'] = slots * 100
        
        return cleaned_data


class BirthdayPartyForm(forms.ModelForm):
    mobile = forms.CharField(
        max_length=15,
        validators=[RegexValidator(r'^\d{10}$', 'Enter a valid 10-digit mobile number')]
    )
    
    class Meta:
        model = BirthdayParty
        fields = ['parent_name', 'child_name', 'child_age', 'mobile', 'email', 
                 'party_date', 'party_time', 'guest_count', 'theme', 
                 'special_requirements', 'package_chosen']
        widgets = {
            'party_date': forms.DateInput(attrs={'type': 'date', 'min': timezone.now().date()}),
            'party_time': forms.TimeInput(attrs={'type': 'time'}),
            'special_requirements': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['parent_name'].widget.attrs.update({'placeholder': 'Parent/Guardian name'})
        self.fields['child_name'].widget.attrs.update({'placeholder': 'Child\'s name'})
        self.fields['mobile'].widget.attrs.update({'placeholder': '10-digit mobile number'})
        self.fields['email'].widget.attrs.update({'placeholder': 'email@example.com'})
        self.fields['theme'].widget.attrs.update({'placeholder': 'e.g., Superhero, Princess, Cartoon'})


class ContactInquiryForm(forms.ModelForm):
    mobile = forms.CharField(
        max_length=15,
        validators=[RegexValidator(r'^\d{10}$', 'Enter a valid 10-digit mobile number')]
    )
    
    class Meta:
        model = ContactInquiry
        fields = ['name', 'email', 'mobile', 'subject', 'message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 4}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'placeholder': 'Your name'})
        self.fields['email'].widget.attrs.update({'placeholder': 'your@email.com'})
        self.fields['mobile'].widget.attrs.update({'placeholder': '10-digit mobile number'})
        self.fields['subject'].widget.attrs.update({'placeholder': 'Subject of your inquiry'})
        self.fields['message'].widget.attrs.update({'placeholder': 'Tell us more about your inquiry...'})
