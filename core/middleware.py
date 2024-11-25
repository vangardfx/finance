from django.utils import timezone
from userauths.views import perform_daily_task
from userauths.models import UserDevice
from user_agents import parse
from django.utils.timezone import now

class AdminTimezoneMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/admin'):
            perform_daily_task()
            timezone.activate('Africa/Lagos')
        else:
            timezone.activate('UTC')

        response = self.get_response(request)

        return response


class DeviceTrackingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if request.user.is_authenticated:
            from .utils import get_device_info  # Assuming you saved the parsing function in utils.py
            device_info = get_device_info(request)
            
            # Track the device
            device, created = UserDevice.objects.get_or_create(
                user=request.user,
                device_name=device_info,
                defaults={'ip_address': get_client_ip(request)}
            )
            if not created:
                device.last_login = now()
                device.save()

            # Enforce limit of 5 devices
            devices = UserDevice.objects.filter(user=request.user).order_by('-last_login')
            if devices.count() > 5:
                devices_to_delete= devices[5:]
                device_ids = devices_to_delete.values_list('id', flat=True)  # Extract IDs
                devices.filter(id__in=device_ids).delete()  # Delete using IDs

        return response

def get_client_ip(request):
    """Helper function to get client IP address."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip