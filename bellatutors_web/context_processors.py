from bellatutors_web.models import ChatMessage, Notification, Order, User
from django.contrib.auth.models import Group
from django.db.models import Q



def new_users(request):
    new_users = User.objects.filter(is_new_user=True)
    return {'new_users': new_users}

def notifications(request):
    notifications = Notification.objects.filter(is_new = True).order_by('-created_at')
    return {'notifications': notifications}


def admin_new_messages(request):
    current_user = request.user
    admin_group = Group.objects.get(name='Admin')
    
    if admin_group in current_user.groups.all():
        admin_new_messages = ChatMessage.objects.filter(is_seen_by_admin=False).exclude(user=current_user).order_by("created_at")
        return {'admin_new_messages': admin_new_messages}
    
    return {'admin_new_messages': None}

def tutor_new_messages(request):
    current_user = request.user
    tutor_group = Group.objects.get(name='Tutor')
    
    if tutor_group in current_user.groups.all():
            tutor_orders = Order.objects.filter(tutor=current_user)

            tutor_new_messages = ChatMessage.objects.filter(
                is_seen_by_tutor=False,
                order__in=tutor_orders,
                order__tutor=current_user,  
            ).exclude(
                Q(user=current_user)
            ).order_by("created_at").distinct()
            return {'tutor_new_messages': tutor_new_messages}
    
    return {'tutor_new_messages': None}

def client_new_messages(request):
    current_user = request.user
    client_group = Group.objects.get(name='Client')
    
    if client_group in current_user.groups.all():
        client_orders = Order.objects.filter(client=current_user)
        client_new_messages = ChatMessage.objects.filter(
        Q(approved=True),
        is_seen_by_client=False,
        order__in=client_orders
    ).exclude(
        Q(user=current_user)
    ).order_by("created_at").distinct()
        return {'client_new_messages': client_new_messages}
    
    return {'client_new_messages': None}
