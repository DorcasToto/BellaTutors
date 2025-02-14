from  bellatutors_web.models import Notification

def create_order_created_notification(order_id, order_title):
    message = f'New Order Created - #{order_id}\nTitle: {order_title}'
    Notification.objects.create(type='Order Created', message=message)

def create_order_approval_notification(order_id, order_title):
    message = f'Order Approved - #{order_id}\nTitle: {order_title}'
    Notification.objects.create(type='Order Approved', message=message)

def create_tutor_creation_notification(tutor_name):
    message = f'Account Creation - Tutor Name: {tutor_name}'
    Notification.objects.create(type='Account Creation', message=message)

def create_tutor_approval_notification(tutor_name):
    message = f'Account Approval - Tutor Name: {tutor_name}'
    Notification.objects.create(type='Account Approval', message=message)