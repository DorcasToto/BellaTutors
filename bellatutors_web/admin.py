from django.contrib import admin
from .models import Instruction, Notification, Payment, Order, Solution, User, ChatMessage
admin.site.register(Order)
admin.site.register(Payment)
admin.site.register(User)
admin.site.register(ChatMessage)
admin.site.register(Solution)
admin.site.register(Instruction)
admin.site.register(Notification)



