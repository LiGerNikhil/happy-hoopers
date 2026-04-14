# Happy Hoopers Play Arena & Café

A Django web application for managing a kids' play arena and café in Vijayawada, India.

## Features

- **Dynamic Content Management**: All content is managed through Django admin
- **Game Management**: Categorized games with pricing and package information
- **Café Menu**: Dynamic menu with stock tracking
- **Booking System**: Cricket slot booking and birthday party reservations
- **Package Management**: Bronze, Silver, and Gold packages
- **Testimonials**: Customer reviews display
- **Gallery**: Photo gallery with categories
- **Contact Forms**: Booking and contact inquiries
- **Responsive Design**: Mobile-friendly interface
- **Admin Dashboard**: Complete content management system

## Installation

### Prerequisites

- Python 3.8+
- pip

### Setup

1. **Clone or download the project to your local directory**

2. **Navigate to the project directory**:
   ```bash
   cd o:/python/clients/chennai_mam/happyhoopers
   ```

3. **Create a virtual environment**:
   ```bash
   python -m venv venv
   ```

4. **Activate the virtual environment**:
   ```bash
   venv\Scripts\activate
   ```

5. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

6. **Run database migrations**:
   ```bash
   python manage.py migrate
   ```

7. **Create a superuser account**:
   ```bash
   python manage.py createsuperuser
   ```

8. **Populate initial data**:
   ```bash
   python manage.py populate_data
   ```

9. **Collect static files**:
   ```bash
   python manage.py collectstatic
   ```

10. **Start the development server**:
    ```bash
    python manage.py runserver
    ```

11. **Access the application**:
    - Frontend: http://127.0.0.1:8000/
    - Admin Panel: http://127.0.0.1:8000/admin/

## Project Structure

```
happyhoopers/
├── arena/                    # Main app
│   ├── models.py            # Database models
│   ├── views.py             # View functions
│   ├── forms.py             # Django forms
│   ├── admin.py             # Admin configuration
│   ├── urls.py              # URL patterns
│   ├── templates/arena/     # HTML templates
│   ├── management/commands/ # Custom management commands
│   └── static/              # Static files
├── happyhoopers/            # Project settings
│   ├── settings.py          # Django settings
│   ├── urls.py              # Main URL configuration
│   └── wsgi.py              # WSGI configuration
├── static/                  # Global static files
│   ├── css/                 # Stylesheets
│   ├── js/                  # JavaScript files
│   └── images/              # Image files
├── media/                   # User uploaded files
├── templates/               # Global templates
├── requirements.txt         # Python dependencies
└── manage.py               # Django management script
```

## Models

The application includes the following main models:

- **GameCategory & Game**: Game categories and individual games
- **CafeCategory & CafeItem**: Café menu categories and items
- **Package**: Pricing packages (Bronze, Silver, Gold)
- **CricketBooking**: Cricket slot bookings
- **BirthdayParty**: Birthday party reservations
- **Testimonial**: Customer reviews
- **ContactInquiry**: Contact form submissions
- **GalleryImage**: Gallery photos
- **SiteSettings**: Site-wide configuration

## Admin Features

The admin panel provides:

- **Game Management**: Add/edit games, categories, pricing
- **Café Management**: Update menu items, track stock
- **Booking Management**: View and manage cricket/bookings
- **Content Management**: Update testimonials, gallery, site settings
- **User Management**: Admin user accounts

## Frontend Features

- **Responsive Design**: Works on all devices
- **Interactive Elements**: Animations, hover effects, transitions
- **Dynamic Loading**: AJAX content loading
- **Form Validation**: Client-side and server-side validation
- **Toast Notifications**: User-friendly feedback messages
- **Gallery Modal**: Image viewing functionality
- **Smooth Scrolling**: Anchor link navigation

## Custom Management Commands

### populate_data

Populates the database with initial data including:
- Game categories and games
- Café categories and menu items
- Pricing packages
- Testimonials
- Site settings
- Gallery images

Usage:
```bash
python manage.py populate_data
```

## Static Files

The project uses organized static files:
- `static/css/style.css`: Main stylesheet with design system
- `static/js/main.js`: JavaScript functionality
- `static/images/`: Image assets

## Templates

- `base.html`: Base template with common elements
- `home.html`: Homepage with all sections
- Additional templates for specific pages (games, packages, etc.)

## Development Notes

- Uses SQLite database for development
- Email backend set to console for development
- Debug mode enabled for development
- Static files served during development
- Media files configured for uploads

## Production Deployment

For production deployment:

1. Set `DEBUG = False` in settings.py
2. Configure proper database (PostgreSQL recommended)
3. Set up static file serving
4. Configure email backend
5. Set up proper domain and SSL
6. Use environment variables for sensitive settings

## Contact

For support or questions:
- Email: admin@happyhoopers.in
- Phone: +91 98765 43210
