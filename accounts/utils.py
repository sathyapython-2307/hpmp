from .models import ActivityLog


def log_activity(user, action, details='', request=None):
    ip = None
    if request:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        ip = x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')
    ActivityLog.objects.create(user=user, action=action, details=details, ip_address=ip)
