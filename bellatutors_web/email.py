from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from bellatutors_web.models import Notification
from bellatutors_web.views.notification_views import create_order_approval_notification, create_order_created_notification, create_tutor_approval_notification, create_tutor_creation_notification

def send_created_order_email(client_name, order_title, order_id, recipients, cc):
    # Creating message subject and sender
    subject = f'New Order Created - #{order_id}'
    sender = 'Bellatutors <support@bellatutors.com>'

    # Passing the context variables
    text_content = render_to_string('email/created_order_email.txt', {'client_name': client_name, 'order_title': order_title})
    html_content = render_to_string('email/created_order_email.html', {'client_name': client_name, 'order_title': order_title})

    msg = EmailMultiAlternatives(subject, text_content, sender, recipients, cc=cc)
    msg.attach_alternative(html_content, 'text/html')
    msg.send()
    # Create a notification after sending the email
    create_order_created_notification(order_id, order_title)

def send_order_approval_email(client_name, order_title, order_id, recipients, cc):
    # Creating unique message subject and sender
    subject = f'Order Approved - #{order_id}'
    sender = 'Bellatutors <support@bellatutors.com>'
    # Passing the context variables
    text_content = render_to_string('email/order_approval.txt', {'client_name': client_name, 'order_title': order_title})
    html_content = render_to_string('email/order_approval.html', {'client_name': client_name, 'order_title': order_title})

    msg = EmailMultiAlternatives(subject, text_content, sender, recipients, cc=cc)
    msg.attach_alternative(html_content, 'text/html')
    msg.send()

    # Create a notification after sending the email
    create_order_approval_notification(order_id, order_title)

def send_new_chat_email(chat_message, chat_written_by, order_title, chat_id, recipients, cc):
    # Creating unique message subject and sender
    subject = f'New chat message notification - #{chat_id}'
    sender = 'Bellatutors <support@bellatutors.com>'
    # Passing the context variables
    text_content = render_to_string('email/new_chat.txt', {'chat_message': chat_message, 'order_title': order_title, 'chat_written_by': chat_written_by})
    html_content = render_to_string('email/new_chat.html', {'chat_message': chat_message, 'order_title': order_title, 'chat_written_by': chat_written_by})

    msg = EmailMultiAlternatives(subject, text_content, sender, recipients, cc=cc)
    msg.attach_alternative(html_content, 'text/html')
    msg.send()

def send_tutor_creation_email(tutor_name, recipients, cc):
    # Creating unique message subject and sender
    subject = f'Account Creation'
    sender = 'Bellatutors <support@bellatutors.com>'
    # Passing the context variables
    text_content = render_to_string('email/tutor_creation.txt', {'tutor_name': tutor_name})
    html_content = render_to_string('email/tutor_creation.html', {'tutor_name': tutor_name})

    msg = EmailMultiAlternatives(subject, text_content, sender, recipients, cc=cc)
    msg.attach_alternative(html_content, 'text/html')
    msg.send()

    # Create a notification after sending the email
    create_tutor_creation_notification(tutor_name)

def send_tutor_approval_email(tutor_name, recipients, cc):
    # Creating unique message subject and sender
    subject = f'Account Approval'
    sender = 'Bellatutors <support@bellatutors.com>'
    # Passing the context variables
    text_content = render_to_string('email/tutor_approval.txt', {'tutor_name': tutor_name})
    html_content = render_to_string('email/tutor_approval.html', {'tutor_name': tutor_name})

    msg = EmailMultiAlternatives(subject, text_content, sender, recipients, cc=cc)
    msg.attach_alternative(html_content, 'text/html')
    msg.send()

    # Create a notification after sending the email
    create_tutor_approval_notification(tutor_name)

