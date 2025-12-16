from django.db import models
from django.contrib.auth.models import User
import uuid

# Create your models here.
class Ticket(models.Model):
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('closed', 'Closed'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='tickets')
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    subject = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, null=False, blank=False)

    def __str__(self):
        if self.user:
            return f"{self.subject} by {self.user.username}"
        else:
            return f"{self.subject} by {self.first_name} {self.last_name}"