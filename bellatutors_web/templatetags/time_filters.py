from django import template
from datetime import datetime
from django.utils import timezone

register = template.Library()

@register.filter
def humanize_time_since(value):
    if not value:
        return "N/A"

    now = timezone.now()
    delta = now - value
    seconds = delta.total_seconds()

    if seconds < 60:
        return f"{int(seconds)} seconds ago"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{int(minutes)} minute{'s' if minutes > 1 else ''} ago"
    elif seconds < 86400:
        hours = seconds / 3600
        return f"{int(hours)} hour{'s' if hours > 1 else ''} ago"
    elif seconds < 31536000:
        days = seconds / 86400
        return f"{int(days)} day{'s' if days > 1 else ''} ago"
    else:
        years = seconds / 31536000
        return f"{int(years)} year{'s' if years > 1 else ''} ago"
