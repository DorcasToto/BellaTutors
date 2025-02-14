from bellatutors_web.email import send_order_approval_email


def send_test_email():
    client_name = 'Dorcas'
    order_title = 'Test Email'
    client_email = 'ngetichnicholas903@gmail.com'
    
    recipients = []
    if client_email:
        recipients.append(client_email)
    
    cc = ["info@bellatutors.com"]
    send_order_approval_email(client_name, order_title, order_id=85, recipients=recipients, cc=cc)
