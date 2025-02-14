from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.fields.files import ImageField
from django.core.validators import MaxLengthValidator, MinLengthValidator
from django.utils import timezone



# Create your models here.
class User(AbstractUser):
    first_name = models.CharField(max_length=144, blank=True, null=True)
    last_name = models.CharField(max_length=144, blank=True, null=True)
    email = models.EmailField(unique=True)
    profile_picture = ImageField(upload_to="profiles", null=True, blank=True)
    phone = models.CharField(
        max_length=13,
        null=True,
        blank=True,
        validators=[MinLengthValidator(10), MaxLengthValidator(13)],
    )
    timezone = models.CharField(max_length=100, default='US/Eastern')
    is_new_user = models.BooleanField(default=True)


    def save_user(self):
        self.save()

    def delete_user(self):
        self.delete()

    def __str__(self):
        return self.username
    

class Category(models.Model):
    name = models.CharField(max_length=200)
    def save_category(self):
        self.save()

    def delete_category(self):
        self.delete()
        
    def __str__(self):
        return self.name
    
class Instruction(models.Model):
    name = models.CharField(max_length=200)
    order = models.ForeignKey("Order", on_delete=models.CASCADE, related_name='instruction_files')
    file = models.FileField(upload_to="uploads/instructions")

    def save_instruction(self):
        self.save()

    def delete_instruction(self):
        self.delete()
        
    def __str__(self):
        return self.name

class Solution(models.Model):
    name = models.CharField(max_length=200)
    order = models.ForeignKey("Order", on_delete=models.CASCADE, related_name='solution_files')
    file = models.FileField(upload_to="uploads/solutions")

    def save_solution(self):
        self.save()

    def delete_solution(self):
        self.delete()

    def __str__(self):
        return self.name
    
class Order(models.Model):
    title = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE,null=True, blank=True) 
    # Status choices
    PENDING = 'Pending'
    IN_PROGRESS = 'In Progress'
    COMPLETED = 'Completed'
    CANCELLED = 'Cancelled'

    STATUS_CHOICES = (
        (PENDING, 'Pending'),
        (IN_PROGRESS, 'In Progress'),
        (COMPLETED, 'Completed'),
        (CANCELLED, 'Cancelled'),
    )

    tutor = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True, related_name="tutor"
    )
    client = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True, related_name="owner"
    )
    description = models.TextField()
    instructions =models.ForeignKey('Instruction',on_delete=models.CASCADE, null=True, blank=True,related_name='orders')
    solutions = models.ForeignKey('Solution',on_delete=models.CASCADE, null=True, blank=True,related_name='orders')
    price = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    tutor_price = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    due_at = models.DateTimeField(null=True,blank= True)
    approved = models.BooleanField(default=False)
    paid = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    def save_order(self):
        self.save()

    def delete_order(self):
        self.delete()

    def __str__(self):
        return self.title

class ChatMessage(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    approved = models.BooleanField(default=False)
    is_seen_by_admin = models.BooleanField(default=False)
    is_seen_by_tutor = models.BooleanField(default=False)
    is_seen_by_client = models.BooleanField(default=False)


    def approve_chat(self):
        self.approved = True
        self.save()

    def save_chat(self):
        self.save()

    def delete_chat(self):
        self.delete()

    def __str__(self):
        return f"Chat for Order titled {self.order.title}"

class Payment(models.Model):
    client = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(default=timezone.now)


class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('Order Created', 'New Order Created'),
        ('Order Approved', 'Order Approved'),
        ('Account Creation', 'Account Creation'),
        ('Account Approval', 'Account Approval'),
    )

    type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_new = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.type}: {self.message}"