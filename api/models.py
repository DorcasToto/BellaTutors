from django.db import models

class Ticket(models.Model):
    sid = models.CharField(max_length=50)
    creator_handle = models.CharField(max_length=50, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    category = models.CharField(max_length=50, null=True, blank=True)
    log_agent = models.CharField(max_length=50, null=True, blank=True)
    summary = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=50, null=True, blank=True)
    customer = models.CharField(max_length=50, null=True, blank=True)
    ticket_type = models.CharField(max_length=50, null=True, blank=True)
    priority = models.IntegerField(null=True, blank=True, default=0)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    problem_id = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return f"{self.summary}"