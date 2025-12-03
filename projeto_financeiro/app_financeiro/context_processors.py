from .models import Notification


def notifications_processor(request):
    """
    Adiciona notificações ao contexto de todos os templates
    """
    if request.user.is_authenticated:
        recent_notifications = Notification.objects.filter(
            user=request.user
        ).order_by('-created_at')[:10]
        
        unread_count = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).count()
        
        return {
            'recent_notifications': recent_notifications,
            'unread_count': unread_count,
        }
    
    return {
        'recent_notifications': [],
        'unread_count': 0,
    }