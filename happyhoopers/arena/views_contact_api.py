from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import ContactInfo

@csrf_exempt
def admin_contact_info_api(request):
    """API for managing contact information"""
    if request.method == 'GET':
        # Get contact info
        contact_info = ContactInfo.get_contact_info()
        
        contact_data = {
            'id': contact_info.id,
            'phone': contact_info.phone,
            'email': contact_info.email,
            'address': contact_info.address,
            'whatsapp': contact_info.whatsapp or '',
            'facebook': contact_info.facebook or '',
            'instagram': contact_info.instagram or '',
            'youtube': contact_info.youtube or '',
            'google_maps_url': contact_info.google_maps_url or '',
            'working_hours': contact_info.working_hours,
            'emergency_contact': contact_info.emergency_contact or '',
            'updated_at': contact_info.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
        }
        
        return JsonResponse({'contact_info': contact_data})
    
    elif request.method == 'PUT':
        # Update contact info
        try:
            data = json.loads(request.body)
            contact_info = ContactInfo.get_contact_info()
            
            contact_info.phone = data.get('phone', contact_info.phone)
            contact_info.email = data.get('email', contact_info.email)
            contact_info.address = data.get('address', contact_info.address)
            contact_info.whatsapp = data.get('whatsapp', contact_info.whatsapp)
            contact_info.facebook = data.get('facebook', contact_info.facebook)
            contact_info.instagram = data.get('instagram', contact_info.instagram)
            contact_info.youtube = data.get('youtube', contact_info.youtube)
            contact_info.google_maps_url = data.get('google_maps_url', contact_info.google_maps_url)
            contact_info.working_hours = data.get('working_hours', contact_info.working_hours)
            contact_info.emergency_contact = data.get('emergency_contact', contact_info.emergency_contact)
            
            contact_info.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Contact information updated successfully!',
                'contact_info': {
                    'phone': contact_info.phone,
                    'email': contact_info.email,
                    'updated_at': contact_info.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
                }
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=400)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)
