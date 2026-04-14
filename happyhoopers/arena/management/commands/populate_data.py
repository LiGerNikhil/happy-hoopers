from django.core.management.base import BaseCommand
from django.db import transaction
from arena.models import (
    GameCategory, Game, CafeCategory, CafeItem, Package,
    Testimonial, SiteSettings, GalleryImage
)


class Command(BaseCommand):
    help = 'Populate the database with initial data for Happy Hoopers'

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write('Populating initial data...')
        
        # Clear existing data
        self.stdout.write('Clearing existing data...')
        Game.objects.all().delete()
        GameCategory.objects.all().delete()
        CafeItem.objects.all().delete()
        CafeCategory.objects.all().delete()
        Package.objects.all().delete()
        Testimonial.objects.all().delete()
        SiteSettings.objects.all().delete()
        GalleryImage.objects.all().delete()
        
        # Create Game Categories
        self.stdout.write('Creating game categories...')
        adventure = GameCategory.objects.create(
            name='Adventure', emoji='🏃', tag_class='adventure'
        )
        sports = GameCategory.objects.create(
            name='Sports', emoji='⚽', tag_class='sports'
        )
        arcade = GameCategory.objects.create(
            name='Arcade', emoji='🎮', tag_class='arcade'
        )
        creative = GameCategory.objects.create(
            name='Creative', emoji='🎨', tag_class='creative'
        )
        
        # Create Games
        self.stdout.write('Creating games...')
        games_data = [
            {
                'name': 'Trampoline Jump',
                'category': adventure,
                'description': 'Jump high and perform tricks on our safe, spring-loaded trampolines.',
                'duration': 'Unlimited',
                'age_group': '5–13',
                'price_info': 'Incl. Gold',
                'package': 'gold',
                'image_url': '/static/images/trampoline.jpg',
                'is_popular': True,
                'order': 1
            },
            {
                'name': 'Ball Pit Splash',
                'category': adventure,
                'description': 'Dive into our colorful ball pit and swim through thousands of soft balls.',
                'duration': '30 min',
                'age_group': '2–8',
                'price_info': 'Incl. Silver',
                'package': 'silver',
                'image_url': '/static/images/ball-pit.jpg',
                'is_popular': True,
                'order': 2
            },
            {
                'name': 'Foam Pit',
                'category': adventure,
                'description': 'Experience the thrill of jumping into a pit of soft, safe foam blocks.',
                'duration': 'Unlimited',
                'age_group': '4–12',
                'price_info': 'Incl. Gold',
                'package': 'gold',
                'image_url': '/static/images/foam-pit.jpg',
                'order': 3
            },
            {
                'name': 'Climbing Wall',
                'category': adventure,
                'description': 'Challenge yourself on our safe, supervised climbing wall with different difficulty levels.',
                'duration': '30 min',
                'age_group': '6–13',
                'price_info': 'Incl. Silver',
                'package': 'silver',
                'image_url': '/static/images/climbing-wall.jpg',
                'order': 4
            },
            {
                'name': 'Cricket Bowling Machine',
                'category': sports,
                'description': 'Practice your batting skills against our automated bowling machine with adjustable speeds.',
                'duration': '15 min',
                'age_group': '6–13',
                'price_info': '₹100/15 min',
                'package': 'individual',
                'image_url': '/static/images/cricket-machine.jpg',
                'is_popular': True,
                'order': 5
            },
            {
                'name': 'Basketball Hoop',
                'category': sports,
                'description': 'Shoot hoops and practice your basketball skills on our adjustable hoops.',
                'duration': 'Unlimited',
                'age_group': '5–13',
                'price_info': 'Incl. Bronze',
                'package': 'bronze',
                'image_url': '/static/images/basketball.jpg',
                'order': 6
            },
            {
                'name': 'Racing Cars',
                'category': arcade,
                'description': 'Race against friends on our electric racing car track.',
                'duration': '10 min',
                'age_group': '4–10',
                'price_info': '₹50/ride',
                'package': 'individual',
                'image_url': '/static/images/racing-cars.jpg',
                'order': 7
            },
            {
                'name': 'Video Games',
                'category': arcade,
                'description': 'Play age-appropriate video games on our gaming consoles.',
                'duration': '30 min',
                'age_group': '6–13',
                'price_info': 'Incl. Bronze',
                'package': 'bronze',
                'image_url': '/static/images/video-games.jpg',
                'order': 8
            },
            {
                'name': 'Art & Craft Station',
                'category': creative,
                'description': 'Express your creativity with various art supplies and guided activities.',
                'duration': '45 min',
                'age_group': '3–10',
                'price_info': 'Incl. Silver',
                'package': 'silver',
                'image_url': '/static/images/art-craft.jpg',
                'order': 9
            },
            {
                'name': 'Building Blocks',
                'category': creative,
                'description': 'Build amazing structures with our collection of blocks and construction toys.',
                'duration': 'Unlimited',
                'age_group': '3–8',
                'price_info': 'Incl. Bronze',
                'package': 'bronze',
                'image_url': '/static/images/building-blocks.jpg',
                'order': 10
            }
        ]
        
        for game_data in games_data:
            Game.objects.create(**game_data)
        
        # Create Cafe Categories
        self.stdout.write('Creating cafe categories...')
        beverages = CafeCategory.objects.create(
            name='Beverages', emoji='🥤', tag_class='cp-bev'
        )
        snacks = CafeCategory.objects.create(
            name='Snacks', emoji='🍿', tag_class='cp-snack'
        )
        combos = CafeCategory.objects.create(
            name='Combos', emoji='🍱', tag_class='cp-combo'
        )
        desserts = CafeCategory.objects.create(
            name='Desserts', emoji='🧁', tag_class='cp-dessert'
        )
        
        # Create Cafe Items
        self.stdout.write('Creating cafe items...')
        cafe_items_data = [
            {
                'name': 'Fresh Orange Juice',
                'category': beverages,
                'description': 'Freshly squeezed orange juice, no added sugar.',
                'price': 80.00,
                'stock_quantity': 20,
                'image_url': '/static/images/orange-juice.jpg',
                'order': 1
            },
            {
                'name': 'Lemon Mint Cooler',
                'category': beverages,
                'description': 'Refreshing lemon juice with fresh mint leaves.',
                'price': 70.00,
                'stock_quantity': 15,
                'image_url': '/static/images/lemon-mint.jpg',
                'order': 2
            },
            {
                'name': 'French Fries',
                'category': snacks,
                'description': 'Crispy golden french fries with seasoning.',
                'price': 120.00,
                'stock_quantity': 30,
                'image_url': '/static/images/french-fries.jpg',
                'order': 3
            },
            {
                'name': 'Popcorn',
                'category': snacks,
                'description': 'Buttered popcorn, perfect for movie time.',
                'price': 60.00,
                'stock_quantity': 25,
                'image_url': '/static/images/popcorn.jpg',
                'order': 4
            },
            {
                'name': 'Kids Meal Combo',
                'category': combos,
                'description': 'Mini burger + fries + juice + toy surprise.',
                'price': 200.00,
                'stock_quantity': 10,
                'image_url': '/static/images/kids-combo.jpg',
                'order': 5
            },
            {
                'name': 'Family Pack',
                'category': combos,
                'description': '2 burgers + 2 fries + 2 juices + 1 dessert.',
                'price': 650.00,
                'stock_quantity': 8,
                'image_url': '/static/images/family-pack.jpg',
                'order': 6
            },
            {
                'name': 'Chocolate Cake Slice',
                'category': desserts,
                'description': 'Moist chocolate cake with rich chocolate frosting.',
                'price': 90.00,
                'stock_quantity': 12,
                'image_url': '/static/images/chocolate-cake.jpg',
                'order': 7
            },
            {
                'name': 'Ice Cream Sundae',
                'category': desserts,
                'description': 'Vanilla ice cream with chocolate sauce and toppings.',
                'price': 100.00,
                'stock_quantity': 18,
                'image_url': '/static/images/ice-cream.jpg',
                'order': 8
            }
        ]
        
        for item_data in cafe_items_data:
            CafeItem.objects.create(**item_data)
        
        # Create Packages
        self.stdout.write('Creating packages...')
        packages_data = [
            {
                'name': 'Bronze Package',
                'tagline': 'Perfect for quick fun and games',
                'price': 299.00,
                'duration': '2 hours',
                'features': [
                    'Access to basic games',
                    'Building blocks area',
                    'Video games station',
                    'Basketball hoop',
                    'Complimentary water bottle'
                ],
                'color_scheme': 'bronze',
                'order': 1
            },
            {
                'name': 'Silver Package',
                'tagline': 'More games, more fun, more memories',
                'price': 499.00,
                'duration': '3 hours',
                'features': [
                    'All Bronze package features',
                    'Trampoline access',
                    'Ball pit unlimited',
                    'Climbing wall session',
                    'Art & craft station',
                    '1 complimentary snack'
                ],
                'color_scheme': 'silver',
                'is_featured': True,
                'order': 2
            },
            {
                'name': 'Gold Package',
                'tagline': 'The ultimate Happy Hoopers experience',
                'price': 799.00,
                'duration': 'Full day',
                'features': [
                    'All Silver package features',
                    'Foam pit unlimited access',
                    'Cricket bowling machine (15 min)',
                    'Racing cars (2 rides)',
                    'Art & craft unlimited',
                    'Complimentary meal',
                    'Birthday crown & photo session',
                    'Party favor bag'
                ],
                'color_scheme': 'gold',
                'order': 3
            }
        ]
        
        for package_data in packages_data:
            Package.objects.create(**package_data)
        
        # Create Testimonials
        self.stdout.write('Creating testimonials...')
        testimonials_data = [
            {
                'name': 'Priya Reddy',
                'role': 'Mom of 2',
                'rating': 5,
                'review_text': 'Amazing place! Kids had so much fun. The staff is very attentive and the place is super clean and safe. We celebrated my son\'s birthday here and it was perfect!',
                'avatar_emoji': '👩',
                'order': 1
            },
            {
                'name': 'Rahul Kumar',
                'role': 'Dad · Gold Package',
                'rating': 5,
                'review_text': 'Best play arena in Vijayawada! The cricket bowling machine is my son\'s favorite. Worth every penny. We come here every weekend.',
                'avatar_emoji': '👨',
                'order': 2
            },
            {
                'name': 'Anjali Sharma',
                'role': 'Mom of 1',
                'rating': 5,
                'review_text': 'Very well maintained and hygienic. The food at the café is fresh and reasonably priced. My daughter loves the trampoline!',
                'avatar_emoji': '👩‍🦰',
                'order': 3
            },
            {
                'name': 'Suresh Babu',
                'role': 'Uncle · Birthday Party',
                'rating': 5,
                'review_text': 'Organized my nephew\'s birthday party here. Excellent service, great food, and the kids had a blast. Highly recommend for birthday celebrations.',
                'avatar_emoji': '👨‍💼',
                'order': 4
            },
            {
                'name': 'Meena Patel',
                'role': 'Mom of 3',
                'rating': 4,
                'review_text': 'Great place for kids to burn energy. The packages are well designed and offer good value. Staff is friendly and helpful.',
                'avatar_emoji': '👩‍👧‍👦',
                'order': 5
            },
            {
                'name': 'Vikram Singh',
                'role': 'Dad · Regular Visitor',
                'rating': 5,
                'review_text': 'The safety measures here are top-notch. As a parent, I feel completely comfortable letting my kids play here. Clean, safe, and fun!',
                'avatar_emoji': '👨‍👧',
                'order': 6
            }
        ]
        
        for testimonial_data in testimonials_data:
            Testimonial.objects.create(**testimonial_data)
        
        # Create Site Settings
        self.stdout.write('Creating site settings...')
        settings_data = [
            {
                'key': 'phone_number',
                'value': '+91 98765 43210',
                'description': 'Main contact phone number'
            },
            {
                'key': 'whatsapp_number',
                'value': '919876543210',
                'description': 'WhatsApp number for bookings'
            },
            {
                'key': 'address',
                'value': 'Gannavaram, Vijayawada, Andhra Pradesh 521101',
                'description': 'Physical address of the arena'
            },
            {
                'key': 'hours',
                'value': '10AM – 10PM Daily',
                'description': 'Operating hours'
            },
            {
                'key': 'facebook_url',
                'value': 'https://facebook.com/happyhoopers',
                'description': 'Facebook page URL'
            },
            {
                'key': 'instagram_url',
                'value': 'https://instagram.com/happyhoopers',
                'description': 'Instagram page URL'
            },
            {
                'key': 'youtube_url',
                'value': 'https://youtube.com/@happyhoopers',
                'description': 'YouTube channel URL'
            },
            {
                'key': 'footer_description',
                'value': 'Vijayawada\'s most loved kids\' play arena and café. Creating epic memories for children and families since day one.',
                'description': 'Footer description text'
            },
            {
                'key': 'announcement_text',
                'value': 'Weekend Special: Get 20% off on Gold Package!',
                'description': 'Announcement bar text'
            },
            {
                'key': 'announcement_label',
                'value': '🎯 Weekend Special',
                'description': 'Announcement bar label'
            },
            {
                'key': 'announcement_link',
                'value': '/packages/',
                'description': 'Announcement bar link'
            }
        ]
        
        for setting_data in settings_data:
            SiteSettings.objects.create(**setting_data)
        
        # Create Gallery Images
        self.stdout.write('Creating gallery images...')
        gallery_data = [
            {
                'title': 'Kids playing on trampolines',
                'description': 'Children having fun on our safe trampoline zone',
                'image_url': '/static/images/gallery/trampoline-fun.jpg',
                'category': 'games',
                'order': 1
            },
            {
                'title': 'Birthday celebration',
                'description': 'Happy birthday party in progress',
                'image_url': '/static/images/gallery/birthday-party.jpg',
                'category': 'birthday',
                'order': 2
            },
            {
                'title': 'Cricket practice session',
                'description': 'Kids practicing batting skills',
                'image_url': '/static/images/gallery/cricket-session.jpg',
                'category': 'games',
                'order': 3
            },
            {
                'title': 'Café area',
                'description': 'Parents relaxing at our café',
                'image_url': '/static/images/gallery/cafe-area.jpg',
                'category': 'cafe',
                'order': 4
            },
            {
                'title': 'Ball pit fun',
                'description': 'Children enjoying the colorful ball pit',
                'image_url': '/static/images/gallery/ball-pit-fun.jpg',
                'category': 'games',
                'order': 5
            },
            {
                'title': 'Play arena entrance',
                'description': 'Welcome to Happy Hoopers',
                'image_url': '/static/images/gallery/entrance.jpg',
                'category': 'facility',
                'order': 6
            }
        ]
        
        for gallery_item in gallery_data:
            GalleryImage.objects.create(**gallery_item)
        
        self.stdout.write(self.style.SUCCESS('Successfully populated initial data!'))
        self.stdout.write('\nData created:')
        self.stdout.write(f'- Game Categories: {GameCategory.objects.count()}')
        self.stdout.write(f'- Games: {Game.objects.count()}')
        self.stdout.write(f'- Cafe Categories: {CafeCategory.objects.count()}')
        self.stdout.write(f'- Cafe Items: {CafeItem.objects.count()}')
        self.stdout.write(f'- Packages: {Package.objects.count()}')
        self.stdout.write(f'- Testimonials: {Testimonial.objects.count()}')
        self.stdout.write(f'- Site Settings: {SiteSettings.objects.count()}')
        self.stdout.write(f'- Gallery Images: {GalleryImage.objects.count()}')
