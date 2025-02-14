from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from rest_framework.decorators import api_view
import re
from django.core.mail import send_mail

import random
import string


from .models import Ticket
from xml.etree import ElementTree
from xml.etree import ElementTree as ET

def generate_random_sid():
    return ''.join(random.choices(string.digits, k=9))

def generate_random_user_handle():
    prefix = 'cnt:'
    random_chars = ''.join(random.choices(string.ascii_uppercase + string.digits, k=32 - len(prefix)))
    return prefix + random_chars

@csrf_exempt
@api_view(['POST'])
def login(request):
    try:
        xml_data = ElementTree.fromstring(request.body)
        username = xml_data.findtext('.//username')
        password = xml_data.findtext('.//password')

        # Mock authentication 
        # If authentication is successful, generate a random SID
        if username == 'sn021607' and password == 'xxxxxxxxxxx':
            sid = generate_random_sid()
            return Response({"SID": sid})
        else:
            return Response({"error": "Invalid credentials"}, status=401)
    except Exception as e:
        return Response({"error": str(e)}, status=500)

@csrf_exempt
@api_view(['POST'])
def get_user_handle(request):
    try:
        xml_data = ElementTree.fromstring(request.body)
        sid = xml_data.findtext('.//sid')
        userID = xml_data.findtext('.//userID')

        if sid and userID:
            # For demonstration purposes, generate a random user handle
            user_handle = generate_random_user_handle()
            return Response({"user_handle": user_handle})
        else:
            return Response({"error": "Invalid credentials"}, status=401)
        
    except Exception as e:
        return Response({"error": str(e)}, status=500)


@csrf_exempt
def create_ticket(request):
    if request.method == 'POST':
        try:
            # Get the XML data from the request body
            xml_data = ET.fromstring(request.body)
            ticket_data = {
                'sid': xml_data.findtext('.//sid'),
                'creator_handle': xml_data.findtext('.//creatorHandle'),
                'description': None,
                'category': None,
                'log_agent': None,
                'summary': None,
                'status': None,
                'customer': None,
                'ticket_type': None,
                'priority': None,
            }

            xml_string = request.body.decode('utf-8')

            pattern = r'<string>(.*?)</string>\s*<string>(.*?)</string>'
            matches = re.findall(pattern, xml_string)

            for field, value in matches:
                if field == 'description':
                    ticket_data['description'] = value
                elif field == 'category':
                    ticket_data['category'] = value
                elif field == 'log_agent':
                    ticket_data['log_agent'] = value
                elif field == 'summary':
                    ticket_data['summary'] = value
                elif field == 'status':
                    ticket_data['status'] = value
                elif field == 'customer':
                    ticket_data['customer'] = value
                elif field == 'type':
                    ticket_data['ticket_type'] = value
                elif field == 'priority':
                    ticket_data['priority'] = value

            ticket = Ticket.objects.create(**ticket_data)
            ticket.save()

            return JsonResponse({'message': 'Ticket created successfully'}, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)


@api_view(['POST'])
def webhook(request):
    if request.method == 'POST':
        data = request.data
        print("Received JSON payload:")
        print(data)
        
        # Convert the JSON payload to a string
        payload_string = str(data)
        
        # Email configuration
        sender_email = "Bellatutors <support@bellatutors.com>" 
        recipients = ["nngetich@ncgafrica.com"] 
        cc = []  
        
        # Send email
        send_mail("New Webhook Payload", payload_string, sender_email, recipients, cc)
        
        return Response({"message": "Payload received successfully"})
    else:
        return Response({"error": "Only POST requests are allowed"}, status=405)
