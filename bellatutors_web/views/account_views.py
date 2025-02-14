from django.contrib.auth.decorators import login_required

from bellatutors_web.email import send_tutor_creation_email
from ..models import Order, Payment
from django.contrib import messages
from ..forms import *

from django.contrib.auth import authenticate
from django.shortcuts import render, redirect, get_object_or_404, HttpResponseRedirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as auth_login

from django.http import HttpResponse, Http404
from django.contrib.auth.models import Group

from django.contrib.auth import logout



from ..forms import *

# @login_required

def register(request):
    return render(request,'accounts/register.html')

def index(request):
  current = request.user
  if current.groups.filter(name="Admin").exists():
      return redirect('admin_home')
  elif current.groups.filter(name="Tutor").exists():
      return redirect('tutor_home')
  elif current.groups.filter(name="Client").exists():
      return redirect('client_home')
  return render(request, 'accounts/home.html')

def terms_and_conditions(request):
  current = request.user
  return render(request, 'accounts/terms_and_conditions.html')

def privacy_policy(request):
  current = request.user
  return render(request, 'accounts/privacy_policy.html')

def register_tutor(request):
    if request.method=='POST':
        signup_form=UserSignUpForm(request.POST)
        if signup_form.is_valid():
            timezone_offset = request.POST.get('timezone_offset')
            user=signup_form.save(commit=False)
            user.is_active = False
            user.timezone = timezone_offset
            user.save()
            group, created = Group.objects.get_or_create(name='Tutor')
            group = Group.objects.get(name = 'Tutor')
            user.groups.add(group)
            user.refresh_from_db()
            tutor_name=user.username
            tutor_email= user.email
            recipients = [tutor_email,]
            cc=["info@bellatutors.com",]
            send_tutor_creation_email(tutor_name,recipients=recipients, cc=cc)
            return redirect('login')
    else:
        signup_form = UserSignUpForm()
    return render(request, 'accounts/signup.html', {'signup_form': signup_form})

def register_client(request):
    if request.method=='POST':
        signup_form=UserSignUpForm(request.POST)
        if signup_form.is_valid():
            timezone_offset = request.POST.get('timezone_offset')
            user=signup_form.save(commit=False)
            user.timezone = timezone_offset
            user.save()
            group, created = Group.objects.get_or_create(name='Client')
            group = Group.objects.get(name = 'Client')
            user.groups.add(group)
            user.refresh_from_db()
            return redirect('login')
    else:
        signup_form = UserSignUpForm()
    return render(request, 'accounts/signup.html', {'signup_form': signup_form})

def login(request):
  if request.method == 'POST':
    form = AuthenticationForm(request=request, data=request.POST)
    if form.is_valid():
      username = form.cleaned_data.get('username')
      password = form.cleaned_data.get('password')
      user = authenticate(username=username, password=password)
      if user is not None:
        auth_login(request, user)
        messages.info(request, f"You are now logged in as {username}")
        return redirect('index')

      else:
        messages.error(request, "Invalid username or password.")
    else:
      messages.error(request, "Invalid username or password.")
  form = AuthenticationForm()
  return render(request = request,template_name = "accounts/login.html",context={"form":form})

def logout_view(request):
    logout(request)
    return redirect('index')

@login_required
def profile(request):
  current_user = request.user

  return render(request,'profile/profile.html',{"current_user":current_user})

@login_required
def update_profile(request):
  if request.method == 'POST':
    user_form = UpdateUserForm(request.POST,request.FILES,instance=request.user)
    if user_form.is_valid():
      user_form.save()
      messages.success(request,'Your Profile has been updated successfully')
      return redirect('profile')
  else:
    user_form = UpdateUserForm(instance=request.user)
  params = {
    'user_form':user_form,
  }
  return render(request,'profile/update.html',params)