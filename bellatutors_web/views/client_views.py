from django.http import HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
import requests

from bellatutors_web.decorators import allowed_users
from bellatutors_web.email import send_created_order_email
from bellatutors_web.views.admin_views import get_cashapp_payment_link
from bellatutors_web.views.shared_views import get_date_range_from_session_or_default
from ..models import Order, Payment
from django.contrib import messages
from ..forms import *

from django.shortcuts import render, redirect, get_object_or_404, HttpResponseRedirect

from ..forms import *
from datetime import datetime,timedelta
from django.db.models import Q


# Calculate the date 7 days ago from today
seven_days_ago = datetime.now() - timedelta(days=7)


@login_required
@allowed_users(allowed_roles=["Admin", "Client"])
def client_home(request):
    start_date, end_date = get_date_range_from_session_or_default(request)
    user = request.user
    unpaid_orders = Order.objects.filter(client=user, paid=False, created_at__range=[start_date, end_date])
    pending_orders = Order.objects.filter(client=user, status='Pending', created_at__range=[start_date, end_date])
    in_progress_orders = Order.objects.filter(client=user, approved=True, created_at__range=[start_date, end_date]).exclude(
        status="Completed"
    )
    completed_orders = Order.objects.filter(
        client=user, approved=True, status="Completed", created_at__range=[start_date, end_date]
    )

    return render(
        request,
        "client/client_home.html",
        {
            "unpaid_orders": unpaid_orders,
            "in_progress_orders": in_progress_orders,
            'pending_orders': pending_orders,
            "completed_orders": completed_orders,
            "start_date": start_date,
            "end_date": end_date - timedelta(days=1),
        },
    )


@login_required
@allowed_users(allowed_roles=["Admin", "Client"])
def client_unpaid_orders_list(request):
    title = "Unpaid Orders"
    start_date, end_date = get_date_range_from_session_or_default(request)
    orders = Order.objects.filter(client=request.user,paid=False,created_at__range=[start_date, end_date]).all()
    return render(request, "client/client_orders_list.html", {"orders": orders,'start_date': start_date,'end_date': end_date - timedelta(days=1),"title":title})

@login_required
@allowed_users(allowed_roles=["Admin", "Client"])
def client_pending_orders_list(request):
    title = "Pending Orders"
    # Retrieve the date range from the session
    start_date, end_date = get_date_range_from_session_or_default(request)
    # Filter orders for the selected date range and status
    orders = Order.objects.filter(
        client=request.user,
        status="Pending",
        created_at__range=[start_date, end_date]
    ).order_by("-created_at")

    return render(request, 'client/client_orders_list.html', {'orders': orders,'start_date': start_date,'end_date': end_date - timedelta(days=1),"title":title})

@login_required
@allowed_users(allowed_roles=["Admin", "Client"])
def client_in_progress_orders_list(request):
    title = "Orders In Progress"
    start_date, end_date = get_date_range_from_session_or_default(request)
    orders = Order.objects.filter(client=request.user,
                                  status = "In Progress",
                                  created_at__range=[start_date, end_date]
                                  ).order_by("-created_at")
    return render(request, 'client/client_orders_list.html', {'orders': orders,'start_date': start_date,'end_date': end_date - timedelta(days=1),"title":title})

@login_required
@allowed_users(allowed_roles=["Admin", "Client"])
def client_completed_orders_list(request):
    start_date, end_date = get_date_range_from_session_or_default(request)
    title = "Completed Orders"
    orders = Order.objects.filter(client=request.user,
                                  status = "Completed",
                                  created_at__range=[start_date, end_date]
                                  ).order_by("-created_at")
    return render(request, 'client/client_orders_list.html', {'orders': orders,'start_date': start_date,'end_date': end_date - timedelta(days=1),"title":title})


@login_required
@allowed_users(allowed_roles=["Admin", "Client"])
def client_order_details(request, order_id):
    user = request.user
    order = Order.objects.get(pk=order_id)
    solutions = Solution.objects.filter(order=order).all()
    attachments = Instruction.objects.filter(order=order).all()
    return render(
        request,
        "client/client_order_details.html",
        {"order": order, "solutions": solutions, "attachments": attachments},
    )


@login_required
@allowed_users(allowed_roles=["Admin", "Client"])
def client_create_order(request):
    if request.method == "POST":
        create_order_form = ClientOrderForm(request.POST, request.FILES)
        if create_order_form.is_valid():
            order = create_order_form.save(commit=False)
            order.client = request.user
            order.save()
            messages.success(request, f"New order created!")
            client_name = request.user.username
            order_title = order.title
            client_email = request.user.email
            recipients = [
                client_email,
            ]
            cc = [
                "info@bellatutors.com",
            ]
            send_created_order_email(
                client_name,
                order_title,
                order_id=order.id,
                recipients=recipients,
                cc=cc,
            )
            return redirect("client_unpaid_orders_list")

    else:
        create_order_form = ClientOrderForm()
    return render(
        request,
        "client/client_create_order.html",
        {"create_order_form": create_order_form},
    )


@login_required
@allowed_users(allowed_roles=["Admin", "Client"])
def client_update_order(request, order_id):
    order = Order.objects.get(pk=order_id)
    if request.method == "POST":
        update_order_form = ClientOrderForm(request.POST, request.FILES, instance=order)
        if update_order_form.is_valid():
            update_order_form.save()
            messages.success(request, f"Order updated!")
            return redirect("client_home")
    else:
        update_order_form = ClientOrderForm(instance=order)
    context = {"update_order_form": update_order_form, "order": order}
    return render(request, "client/update_order.html", context)


@login_required
@allowed_users(allowed_roles=["Admin", "Client"])
def client_order_chats(request, order_id):
    current_user = request.user
    order = get_object_or_404(Order, id=order_id)
    chat_messages = ChatMessage.objects.filter(
        models.Q(approved=True) | models.Q(user=current_user), order=order
    ).order_by("created_at")
    if request.method == "POST":
        message = request.POST.get("message")
        if message:
            ChatMessage.objects.create(order=order, user=request.user, message=message)
            return redirect("client_order_chats", order_id=order_id)

    context = {
        "order": order,
        "chat_messages": chat_messages,
    }
    return render(request, "client/order_chats.html", context)


@login_required
@allowed_users(allowed_roles=["Admin", "Client"])
def client_new_messages_list(request):
    current_user = request.user

    client_orders = Order.objects.filter(client=current_user)

    client_new_messages = ChatMessage.objects.filter(
        Q(approved=True),
        is_seen_by_client=False,
        order__in=client_orders
    ).exclude(
        Q(user=current_user)
    ).order_by("created_at").distinct()

    return render(request, 'client/client_new_messages_list.html', {
        'client_new_messages': client_new_messages,
    })


@login_required
@allowed_users(allowed_roles=["Admin", "Client"])
def view_client_new_message(request, client_new_message_id):
    client_new_message = ChatMessage.objects.get(pk=client_new_message_id)
    client_new_message.is_seen_by_client = True
    client_new_message.save()

    # Fetch the associated order for the message
    order = client_new_message.order

    if order:
        return redirect('client_order_chats', order.id)
    else:
        # Handle cases where the associated order is not found
        return HttpResponse("Order not found")
    

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
    return render(request, 'client/upload_instruction.html', context)
