from .models import ContactMessage, AdminNotification

def admin_context(request):
    context = {}
    if request.user.is_staff:
        context['unread_messages_count'] = ContactMessage.objects.filter(is_read=False).count()
        context['unread_notifications_count'] = AdminNotification.objects.filter(user=request.user, is_read=False).count()
        context['notifications'] = AdminNotification.objects.filter(user=request.user).order_by('-created_at')[:5]
    return context
