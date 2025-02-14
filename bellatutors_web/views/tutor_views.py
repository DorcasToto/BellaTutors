from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse

from bellatutors_web.decorators import allowed_users
from bellatutors_web.views.shared_views import get_date_range_from_session_or_default
from ..models import Order, ChatMessage
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404

from ..forms import *
from django.db.models import Q, Sum
from datetime import datetime,timedelta

# Calculate the date 7 days ago from today
seven_days_ago = datetime.now() - timedelta(days=7)

@login_required
@allowed_users(allowed_roles=["Admin", "Tutor"])
def tutor_home(request):
    start_date, end_date = get_date_range_from_session_or_default(request)
    user = request.user
    available_orders = Order.objects.filter(tutor__isnull=True, approved=True, created_at__range=[start_date, end_date])
    in_progress_orders = Order.objects.filter(tutor=user, approved=True, created_at__range=[start_date, end_date]).exclude(
        status="Completed"
    )
    completed_orders = Order.objects.filter(
        tutor=user, approved=True, status="Completed", created_at__range=[start_date, end_date]
    )

    revenue = (
        completed_orders.aggregate(total_revenue=Sum("tutor_price"))["total_revenue"] or 0
    )
    return render(
        request,
        "tutor/tutor_home.html",
        {
            "available_orders": available_orders,
            "in_progress_orders": in_progress_orders,
            "completed_orders": completed_orders,
            "revenue": revenue,
            "start_date": start_date,
            "end_date": end_date - timedelta(days=1),
        },
    )


@login_required
@allowed_users(allowed_roles=["Admin", "Tutor"])
def tutor_available_orders_list(request):
    start_date, end_date = get_date_range_from_session_or_default(request)
    title = "Available Orders"
    orders = Order.objects.filter(
        Q(tutor__isnull=True) & Q(approved=True), 
        approved=True,
        created_at__range=[start_date, end_date]
    )
    return render(request, "tutor/tutor_orders_list.html", {"orders": orders,'start_date': start_date,'end_date': end_date - timedelta(days=1),"title":title})


@login_required
@allowed_users(allowed_roles=["Admin", "Tutor"])
def tutor_in_progress_orders_list(request):
    title = "Orders In Progress"
    start_date, end_date = get_date_range_from_session_or_default(request)
    orders = Order.objects.filter(tutor=request.user,
                                  status = "In Progress",
                                  approved=True,
                                  created_at__range=[start_date, end_date]
                                  ).order_by("-created_at")
    return render(request, 'tutor/tutor_orders_list.html', {'orders': orders,'start_date': start_date,'end_date': end_date - timedelta(days=1),"title":title})

@login_required
@allowed_users(allowed_roles=["Admin", "Tutor"])
def tutor_completed_orders_list(request):
    start_date, end_date = get_date_range_from_session_or_default(request)
    title = "Completed Orders"
    orders = Order.objects.filter(tutor=request.user,
                                  status = "Completed",
                                  approved=True,
                                  created_at__range=[start_date, end_date]
                                  ).order_by("-created_at")
    return render(request, 'tutor/tutor_orders_list.html', {'orders': orders,'start_date': start_date,'end_date': end_date - timedelta(days=1),"title":title})



@login_required
@allowed_users(allowed_roles=["Admin", "Tutor"])
def tutor_order_details(request, order_id):
    user = request.user
    order = Order.objects.get(pk=order_id)
    solutions = Solution.objects.filter(order=order).all()
    attachments = Instruction.objects.filter(order=order).all()
    return render(
        request,
        "tutor/tutor_order_details.html",
        {"order": order, "solutions": solutions, "attachments": attachments},
    )


@login_required
@allowed_users(allowed_roles=["Admin", "Tutor"])
def book_order(request, order_id):
    order = Order.objects.get(pk=order_id)
    if order:
        order.tutor = request.user
        order.status = "In Progress"
        order.save()
        messages.success(request, f"Order booked Successfully!")
    return redirect("tutor_in_progress_orders_list")


@login_required
@allowed_users(allowed_roles=["Admin", "Tutor"])
def upload_solution(request, order_id):
    order = Order.objects.get(pk=order_id)
    if request.method == "POST":
        upload_solution_form = UploadSolutionForm(request.POST, request.FILES)
        if upload_solution_form.is_valid():
            upload = upload_solution_form.save(commit=False)
            upload.order = order
            upload.save()
            order.status = "Completed"
            order.save()
            messages.success(request, f"Solution uploaded successfully!")
            previous_url = request.session.get("previous_url")
            if previous_url:
                del request.session["previous_url"]
                return redirect(previous_url)
    else:
        upload_solution_form = UploadSolutionForm()
        request.session["previous_url"] = request.META.get("HTTP_REFERER")
    context = {"upload_solution_form": upload_solution_form, "order": order}
    return render(request, "tutor/upload_solution.html", context)


@login_required
@allowed_users(allowed_roles=["Admin", "Tutor"])
def tutor_order_chats(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    current_user = request.user
    chat_messages = ChatMessage.objects.filter(
        models.Q(approved=True) | models.Q(user=current_user), order=order
    ).order_by("created_at")

    if request.method == "POST":
        message = request.POST.get("message")
        if message:
            ChatMessage.objects.create(order=order, user=request.user, message=message)
            return redirect("tutor_order_chats", order_id=order_id)

    context = {
        "order": order,
        "chat_messages": chat_messages,
    }
    return render(request, "tutor/order_chats.html", context)


@login_required
@allowed_users(allowed_roles=["Admin", "Tutor"])
def tutor_new_messages_list(request):
    current_user = request.user

    tutor_orders = Order.objects.filter(tutor=current_user)

    tutor_new_messages = ChatMessage.objects.filter(
        Q(approved=True),
        is_seen_by_tutor=False,
        order__in=tutor_orders,
        order__tutor=current_user, 
    ).exclude(
        Q(user=current_user)
    ).order_by("created_at").distinct()

    return render(request, 'tutor/tutor_new_messages_list.html', {
        'tutor_new_messages': tutor_new_messages,
    })


@login_required
@allowed_users(allowed_roles=["Admin", "Tutor"])
def view_tutor_new_message(request, tutor_new_message_id):
    tutor_new_message = ChatMessage.objects.get(pk=tutor_new_message_id)
    tutor_new_message.is_seen_by_tutor = True
    tutor_new_message.save()

    # Fetch the associated order for the message
    order = tutor_new_message.order

    if order:
        return redirect('tutor_order_chats', order.id)
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
    return render(request, 'tutor/upload_solution.html', context)