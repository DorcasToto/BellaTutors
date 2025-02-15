from django.http import HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
import requests
from bellatutors_web.decorators import admin_only, allowed_users
from bellatutors_web.email import  send_created_order_email, send_new_chat_email, send_order_approval_email, send_tutor_approval_email
from bellatutors_web.views.shared_views import get_date_range_from_session_or_default
from ..models import Order, Payment
from django.contrib import messages
from ..forms import *

from django.shortcuts import render, redirect, get_object_or_404, HttpResponseRedirect

from ..forms import *
from django.contrib.auth.models import Group
import pytz
from django.db.models import Q, Sum
from datetime import datetime,timedelta


@login_required
@admin_only
def admin_home(request):
    start_date, end_date = get_date_range_from_session_or_default(request)
    pending_orders = Order.objects.filter(
        status="Pending",
        created_at__range=[start_date, end_date]
    )

    in_progress_orders = Order.objects.filter(
        status="In Progress",
        created_at__range=[start_date, end_date]
    )

    completed_orders = Order.objects.filter(
        approved=True,
        status="Completed",
        created_at__range=[start_date, end_date]
    )

    revenue = completed_orders.aggregate(total_revenue=Sum('price'))['total_revenue'] or 0

    active_users = User.objects.filter(is_active=True)
    unactivated_users = User.objects.filter(is_active=False)
    tutor_users = User.objects.filter(groups__name='Tutor')
    client_users = User.objects.filter(groups__name='Client')

    return render(request, 'admin/admin_home.html', {
        'pending_orders': pending_orders,
        'in_progress_orders': in_progress_orders,
        'completed_orders': completed_orders,
        'revenue': revenue,
        'active_users': active_users,
        'unactivated_users': unactivated_users,
        'tutor_users': tutor_users,
        'client_users': client_users,
        'start_date': start_date,
        'end_date': end_date - timedelta(days=1),
    })

@login_required
@admin_only  
def new_users_list(request):
    new_users = User.objects.filter(is_new_user=True)
    return render(request, 'admin/new_users_list.html', {'users': new_users})

@login_required
@admin_only
def pending_orders_list(request):
    # Retrieve the date range from the session
    start_date, end_date = get_date_range_from_session_or_default(request)
    # Filter orders for the selected date range and status
    orders = Order.objects.filter(
        status="Pending",
        created_at__range=[start_date, end_date]
    ).order_by("-created_at")

    return render(request, 'admin/pending_orders_list.html', {'orders': orders,'start_date': start_date,'end_date': end_date - timedelta(days=1),})

@login_required
@admin_only
def in_progress_orders_list(request):
    start_date, end_date = get_date_range_from_session_or_default(request)
    orders = Order.objects.filter(status = "In Progress",
                                  created_at__range=[start_date, end_date]
                                  ).order_by("-created_at")
    return render(request, 'admin/in_progress_orders_list.html', {'orders': orders,'start_date': start_date,'end_date': end_date - timedelta(days=1),})

@login_required
@admin_only
def completed_orders_list(request):
    start_date, end_date = get_date_range_from_session_or_default(request)
    orders = Order.objects.filter(status = "Completed",
                                  created_at__range=[start_date, end_date]
                                  ).order_by("-created_at")
    return render(request, 'admin/completed_orders_list.html', {'orders': orders,'start_date': start_date,'end_date': end_date - timedelta(days=1),})


@login_required
@admin_only
def tutors_list(request):
    users = User.objects.filter(groups__name='Tutor')
    return render(request, 'admin/users_list.html', {'users': users})

@login_required
@admin_only
def active_users_list(request):
    users = User.objects.filter(is_active=True)
    return render(request, 'admin/users_list.html', {'users': users})

@login_required
@admin_only
def unactivated_users_list(request):
    users = User.objects.filter(is_active=False)
    return render(request, 'admin/users_list.html', {'users': users})

@login_required
@admin_only
def clients_list(request):
    users = User.objects.filter(groups__name='Client')
    return render(request, 'admin/users_list.html', {'users': users})

@login_required
@admin_only
def admins_list(request):
    users = User.objects.filter(groups__name='Admin')
    return render(request, 'admin/users_list.html', {'users': users})


@login_required
@admin_only
def payments(request):
    payments = Payment.objects.all()
    return render(request, 'admin/payments.html', {'payments': payments})

@login_required
@admin_only
def admin_order_details(request,order_id):
    user = request.user
    order = Order.objects.get(pk=order_id)
    solutions = Solution.objects.filter(order = order).all()
    attachments = Instruction.objects.filter(order = order).all()
    return render(request, 'admin/admin_order_details.html', {'order': order, 'solutions': solutions, "attachments": attachments})


@login_required
@admin_only
def create_order(request):
  if request.method == 'POST':
    create_order_form = OrderForm(request.POST,request.FILES)
    if create_order_form.is_valid():
      order = create_order_form.save(commit=False)
      order.approved = True
      order.save()
      client_name = "Not Set"
      order_title = order.title
      recipients = [
          "info@bellatutors.com",
      ]
      cc = []
      send_created_order_email(
          client_name,
          order_title,
          order_id=order.id,
          recipients=recipients,
          cc=cc,
      )
      messages.success(request, f'New order created!')
      return redirect('pending_orders_list')

  else:
    create_order_form = OrderForm()
    
  return render(request, 'admin/create_order.html',{'create_order_form':create_order_form})

@login_required
@admin_only
def update_order(request, order_id):
    order = Order.objects.get(pk=order_id)
    
    if request.method == 'POST':
        update_order_form = OrderUpdateForm(request.POST, request.FILES, instance=order)
        if update_order_form.is_valid():
            update_order_form.save()
            messages.success(request, 'Order updated!')
            previous_url = request.session.get('previous_url')
            if previous_url:
                del request.session['previous_url']
                return redirect(previous_url)
    else:
        update_order_form = OrderUpdateForm(instance=order)
        request.session['previous_url'] = request.META.get('HTTP_REFERER')
    
    context = {
        'update_order_form': update_order_form,
        'order': order
    }
    return render(request, 'admin/update_order.html', context)

@login_required
@admin_only
def approve_order(request, order_id):
    order = Order.objects.get(pk=order_id)
    if order:
        order.approved = True
        order.save()
        messages.success(request, f'Order approved!')
        client_name = order.client.username
        order_title = order.title
        client_email = order.client.email if order.client else None
        
        recipients = []
        if client_email:
            recipients.append(client_email)
        
        cc = ["info@bellatutors.com"]
        send_order_approval_email(client_name, order_title, order_id=order.id, recipients=recipients, cc=cc)
    return redirect(request.META.get('HTTP_REFERER', '/'))


@login_required
@admin_only
def mark_order_as_paid(request,order_id):
  order = Order.objects.get(pk=order_id)
  if order:
    order.paid= True
    order.save()
    messages.success(request, f'Order marked as paid!')
  return redirect(request.META.get('HTTP_REFERER', '/'))

@login_required
@admin_only
def create_user(request):
  if request.method == 'POST':
    create_user_form = CreateUserForm(request.POST,request.FILES)
    if create_user_form.is_valid():
      user = create_user_form.save(commit=False)
      user.save()
      user.groups.set(create_user_form.cleaned_data['groups'])
      messages.success(request, f'New user created!')
      return redirect(request.META.get('HTTP_REFERER', '/'))

  else:
    create_user_form = CreateUserForm()
    
  return render(request, 'admin/create_user.html',{'create_user_form':create_user_form})

@login_required
@admin_only
def update_user(request, user_id):
  user = User.objects.get(pk=user_id)
  if request.method == 'POST':
    update_user_form = AdminUpdateUserForm(request.POST,request.FILES, instance=user)
    if update_user_form.is_valid():
      update_user_form.save()
      messages.success(request, f'User updated!')
      previous_url = request.session.get('previous_url')
      if previous_url:
          del request.session['previous_url']
          return redirect(previous_url)
  else:
    update_user_form = AdminUpdateUserForm(instance=user)
    request.session['previous_url'] = request.META.get('HTTP_REFERER')
  context = {
      "update_user_form":update_user_form,
      "user":user
  }
  return render(request, 'admin/update_user.html', context)

@login_required
@admin_only
def view_new_user(request, user_id):
  user = User.objects.get(pk=user_id)
  user.is_new_user = False
  user.save()
  context = {
      "user":user
  }
  return render(request, 'admin/view_new_user.html', context)

@login_required
@admin_only
def approve_tutor(request,user_id):
  user = User.objects.get(pk=user_id)
  if user:
    user.is_active = True
    user.save()
    messages.success(request, f'Tutor Approved!')
    tutor_name=user.username
    tutor_email= user.email
    recipients = [tutor_email,]
    cc=["info@bellatutors.com",]
    send_tutor_approval_email(tutor_name,recipients=recipients, cc=cc)
  return redirect(request.META.get('HTTP_REFERER', '/'))

@login_required
@admin_only
def delete_user(request,user_id):
  user = User.objects.get(pk=user_id)
  if user:
    user.delete_user()
    messages.success(request, f'User deleted!')
  return redirect(request.META.get('HTTP_REFERER', '/'))

@login_required
@admin_only
def generate_cashapp_payment_link(amount, note):
    cashapp_username = "YOUR_CASH_APP_USERNAME"
    cashapp_access_token = "YOUR_CASH_APP_ACCESS_TOKEN"
    url = f'https://cash.app/api/payments/{cashapp_username}'
    headers = {
        'Authorization': f'Bearer {cashapp_access_token}',
        'Content-Type': 'application/json'
    }
    data = {
        'amount': amount,
        'note': note,
        'action': 'cash-out'
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 201:
        response_data = response.json()
        payment_link = response_data['data']['attributes']['web_url']
        return payment_link
    else:
        response.raise_for_status()
        
@login_required
@admin_only
def get_cashapp_payment_link(amount, note):
    cashapp_payment_link = generate_cashapp_payment_link(amount, note)
    if cashapp_payment_link:
        return f"Click this link to proceed with your payment using Cash App: {cashapp_payment_link}"
    else:
        return "Unable to generate payment link. Please try again later."

@login_required
@admin_only
def order_chats(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    chat_messages = ChatMessage.objects.filter(order=order).order_by("created_at")

    user_timezone = request.user.timezone
    user_tz = pytz.timezone(user_timezone)
    modified_chat_messages = []
    for chat in chat_messages:
        print(f"Original timezone {chat.created_at}")
        utc_time = chat.created_at
        local_time = utc_time.astimezone(user_tz)
        chat.created_at = local_time
        modified_chat_messages.append(chat)

    for chat in modified_chat_messages:
       print(f"Modified {chat.created_at}")


    if request.method == "POST":
        message = request.POST.get("message")
        if message:
            ChatMessage.objects.create(order=order, user=request.user, message=message)
            return redirect('admin_order_chats', order_id=order_id)

    context = {
        "order": order,
        "chat_messages": chat_messages,
    }
    return render(request, "admin/order_chats.html", context)

@login_required
@admin_only
def approve_chat(request, chat_id):
    chat = ChatMessage.objects.get(pk=chat_id)
    if chat:
        chat.approve_chat()
        messages.success(request, f'Chat approved!')
        order_title = chat.order.title
        chat_message = chat.message
        client_email = chat.order.client.email if chat.order.client else None
        chat_written_by = f'{chat.user.first_name} {chat.user.last_name}'
        tutor_email = chat.order.tutor.email if chat.order.tutor else None
        
        recipients = []
        if client_email:
            recipients.append(client_email)
        if tutor_email:
            recipients.append(tutor_email)
        
        cc = ["info@bellatutors.com"]
        send_new_chat_email(chat_message, chat_written_by, order_title, chat_id=chat.id, recipients=recipients, cc=cc)
    return redirect(request.META.get('HTTP_REFERER', '/'))


@login_required
@admin_only
def delete_chat(request,chat_id):
  chat = ChatMessage.objects.get(pk=chat_id)
  if chat:
    chat.delete_chat()
    messages.success(request, f'Chat deleted!')
  return redirect(request.META.get('HTTP_REFERER', '/'))


@login_required
@admin_only
def create_category(request):
  if request.method == 'POST':
    create_category_form = CategoryForm(request.POST)
    if create_category_form.is_valid():
      category = create_category_form.save(commit=False)
      category.save()
      messages.success(request, f'New category created!')
      return redirect('category_list')

  else:
    create_category_form = CategoryForm()
    
  return render(request, 'admin/create_category.html',{'create_category_form':create_category_form})


def category_list(request):
    categories = Category.objects.all().order_by('name')
    return render(request, 'admin/category_list.html', {'categories': categories})

@login_required
@admin_only
def update_category(request, category_id):
  category = Category.objects.get(pk=category_id)
  if request.method == 'POST':
    update_category_form = CategoryForm(request.POST, instance=category)
    if update_category_form.is_valid():
      update_category_form.save()
      messages.success(request, f'Category updated!')
      previous_url = request.session.get('previous_url')
      if previous_url:
          del request.session['previous_url']
          return redirect(previous_url)
  else:
    update_category_form = CategoryForm(instance=category)
    request.session['previous_url'] = request.META.get('HTTP_REFERER')
  context = {
      "update_category_form":update_category_form,
      "category":category
  }
  return render(request, 'admin/update_category.html', context)

@login_required
@admin_only
def delete_category(request,category_id):
  category = Category.objects.get(pk=category_id)
  if category:
    category.delete_category()
    messages.success(request, f'Category deleted!')
  return redirect(request.META.get('HTTP_REFERER', '/'))


@login_required
@admin_only  
def new_notifications_list(request):
    new_notifications = Notification.objects.filter(is_new=True)
    return render(request, 'admin/new_notifications_list.html', {'notifications': new_notifications})

@login_required
@admin_only
def view_new_notification(request, notification_id):
  notification = Notification.objects.get(pk=notification_id)
  notification.is_new = False
  notification.save()
  context = {
      "notification":notification
  }
  return render(request, 'admin/view_new_notification.html', context)


@login_required
@admin_only  
def admin_new_messages_list(request):
    current_user = request.user  

    admin_new_messages = ChatMessage.objects.filter(is_seen_by_admin=False).exclude(user=current_user)
    
    return render(request, 'admin/admin_new_messages_list.html', {
        'admin_new_messages': admin_new_messages,
    })

@login_required
@admin_only
def view_admin_new_message(request, admin_new_message_id):
    admin_new_message = ChatMessage.objects.get(pk=admin_new_message_id)
    admin_new_message.is_seen_by_admin = True
    admin_new_message.save()

    # Fetch the associated order for the message
    order = admin_new_message.order

    if order:
        return redirect('admin_order_chats', order.id)
    else:
        # Handle cases where the associated order is not found
        return HttpResponse("Order not found")
    


@login_required
@allowed_users(allowed_roles=['Admin','Tutor'])
def upload_solution(request, order_id):
    order = Order.objects.get(pk=order_id)
    if request.method == 'POST':
        upload_solution_form = UploadSolutionForm(request.POST,request.FILES)
        if upload_solution_form.is_valid():
            upload = upload_solution_form.save(commit=False)
            upload.order = order
            upload.save()
            order.status = "Completed"
            order.save()
            messages.success(request, f'Solution uploaded successfully!')
            previous_url = request.session.get('previous_url')
            if previous_url:
                del request.session['previous_url']
                return redirect(previous_url)
    else:
        upload_solution_form = UploadSolutionForm()
        request.session['previous_url'] = request.META.get('HTTP_REFERER')
    context = {
        "upload_solution_form":upload_solution_form,
        "order":order
    }
    return render(request, 'admin/upload_solution.html', context)

@login_required
@allowed_users(allowed_roles=['Admin','Client'])
def upload_instruction(request, order_id):
    order = Order.objects.get(pk=order_id)
    if request.method == 'POST':
        upload_instruction_form = UploadInstructionForm(request.POST,request.FILES)
        if upload_instruction_form.is_valid():
            upload = upload_instruction_form.save(commit=False)
            upload.order = order
            upload.save()
            messages.success(request, f'Instruction uploaded successfully!')
            previous_url = request.session.get('previous_url')
            if previous_url:
                del request.session['previous_url']
                return redirect(previous_url)
    else:
        upload_instruction_form = UploadInstructionForm()
        request.session['previous_url'] = request.META.get('HTTP_REFERER')
    context = {
        "upload_instruction_form":upload_instruction_form,
        "order":order
    }
    return render(request, 'admin/upload_instruction.html', context)

####TESTS
@login_required
@admin_only
def ticket_list(request):
    start_date, end_date = get_date_range_from_session_or_default(request)
    tickets = Ticket.objects.filter(created_at__range=[start_date, end_date]).order_by("-created_at")
    return render(request, 'admin/ticket_list.html', {'tickets': tickets,'start_date': start_date,'end_date': end_date - timedelta(days=1),})
