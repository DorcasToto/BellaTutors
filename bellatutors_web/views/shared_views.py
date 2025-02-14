from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from bellatutors_web.decorators import allowed_users
from ..models import Order,ChatMessage
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404

from ..forms import *
from datetime import datetime,timedelta


@login_required
@allowed_users(allowed_roles=['Admin','Tutor'])
def delete_solution(request,solution_id):
  solution = Solution.objects.get(pk=solution_id)
  if solution:
    solution.delete_solution()
    messages.success(request, f'Solution deleted!')
  return redirect(request.META.get('HTTP_REFERER', '/'))

@login_required
@allowed_users(allowed_roles=['Admin','Client'])
def delete_order(request,order_id):
  order = Order.objects.get(pk=order_id)
  if order:
    order.delete_order()
    messages.success(request, f'Order deleted!')
  return redirect('index')

@login_required
@allowed_users(allowed_roles=['Admin','Client'])
def delete_instruction(request,instruction_id):
  instruction = Instruction.objects.get(pk=instruction_id)
  if instruction:
    instruction.delete_instruction()
    messages.success(request, f'Instruction deleted!')
  return redirect(request.META.get('HTTP_REFERER', '/'))


@login_required
@allowed_users(allowed_roles=['Admin', 'Tutor', 'Client'])
def edit_chat(request, message_id):
    message = get_object_or_404(ChatMessage, id=message_id)
    order_id = message.order.id

    if request.method == "POST":
        edited_message = request.POST.get("edited_message")
        if edited_message:
            message.message = edited_message
            message.save()
    
    current_user = request.user
    if current_user.groups.filter(name='Tutor').exists():
        return redirect('tutor_order_chats', order_id=order_id)
    elif current_user.groups.filter(name='Admin').exists():
        return redirect('admin_order_chats', order_id=order_id)
    else:
        return redirect('client_order_chats', order_id=order_id)

@login_required
@allowed_users(allowed_roles=['Admin', 'Tutor', 'Client'])
def set_timeframe(request):
    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        if start_date and end_date:
            # Convert and store the selected date range in the session
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            end_date = end_date + timedelta(days=1)  # Adjust the end date to include the entire day
        else:
            # If either start_date or end_date is missing, use the default date range
            start_date, end_date = get_default_date_range()

        # Store the selected date range in the session
        request.session['start_date'] = start_date.isoformat()
        request.session['end_date'] = end_date.isoformat()

        return redirect(request.META.get('HTTP_REFERER', '/'))
    return JsonResponse({'message': 'Invalid or no timeframe data provided'})

def get_default_date_range(default_days=7):
    # Calculate the default date range, including today but excluding the current day
    end_date = timezone.now().date() + timedelta(days=1)
    start_date = end_date - timedelta(days=default_days)
    return start_date, end_date


def get_date_range_from_session_or_default(request, default_days=7):
    start_date_str = request.session.get('start_date')
    end_date_str = request.session.get('end_date')

    if start_date_str and end_date_str:
        start_date = datetime.fromisoformat(start_date_str).date()
        end_date = datetime.fromisoformat(end_date_str).date()
    else:
        # If no custom date range is set in the session, use the default date range
        start_date, end_date = get_default_date_range()

    return start_date, end_date
