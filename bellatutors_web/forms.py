from django import forms
from django.db.models import fields
from bellatutors_web.models import *
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group


class OrderForm(forms.ModelForm):
  due_at = forms.DateTimeField(
        label='Due At',
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
    )
  tutor = forms.ModelChoiceField(
        queryset=User.objects.filter(groups__name='Tutor'),
        required=False
    )
  price = forms.DecimalField(label='Client Price($)')
  tutor_price = forms.DecimalField(label='Tutor Price(Ksh)')
  class Meta:
    model = Order
    fields = ('title','category','description','tutor','due_at','price','tutor_price','status')

class OrderUpdateForm(forms.ModelForm):
    due_at = forms.DateTimeField(
        label='Due At',
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
    )
    tutor = forms.ModelChoiceField(
        queryset=User.objects.filter(groups__name='Tutor'),
        required=False
    )
    price = forms.DecimalField(label='Client Price($)')
    tutor_price = forms.DecimalField(label='Tutor Price(Ksh)')

    class Meta:
        model = Order
        fields = ('title', 'category', 'description', 'tutor', 'due_at', 'price', 'tutor_price', 'status')


class SolutionUpdateForm(forms.ModelForm):
    class Meta:
        model = Solution
        fields = ('name','file')


class ClientOrderForm(forms.ModelForm):
    due_at = forms.DateTimeField(
        label='Due At',
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
    )
    price = forms.DecimalField(label='Budget($)')

    class Meta:
        model = Order
        fields = ('title', 'category', 'description', 'due_at', 'price')


class UploadSolutionForm(forms.ModelForm):
  class Meta:
    model = Solution
    fields = ('name','file')

class UploadInstructionForm(forms.ModelForm):
    class Meta:
        model = Instruction
        fields = ('name', 'file')
        labels = {
            'name': 'File Name',
        }

class CreateUserForm(UserCreationForm):
    password1 = forms.CharField(label='Enter password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm password', widget=forms.PasswordInput)
    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(),
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email', 'password1', 'password2')
        help_texts = {
            'username': None,
        }


class UserSignUpForm(UserCreationForm):
    password1 = forms.CharField(label='Enter password', 
                                widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm password', 
                                widget=forms.PasswordInput)
    class Meta:
        model=User
        fields=('first_name','last_name',"username","email","password1","password2")
        help_texts = {
            "username":None,
        }

class AdminUpdateUserForm(forms.ModelForm):
  email = forms.EmailField()
  class Meta:
    model = User
    fields = ('first_name', 'last_name', 'email', 'is_active')

class PaymentForm(forms.ModelForm):
  class Meta:
    model = Payment
    fields = ('client','order','amount')

class UpdateUserForm(forms.ModelForm):
  email = forms.EmailField()
  class Meta:
    model = User
    fields = ['first_name','last_name','email','phone','profile_picture']

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = '__all__'