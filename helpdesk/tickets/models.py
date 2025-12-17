from django.db import models
from django.contrib.auth.models import User
import uuid
from django.utils.text import slugify

# Create your models here.
class Company(models.Model):
    name = models.CharField(max_length=35)
    slug = models.SlugField(unique=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Ticket(models.Model):
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('closed', 'Closed'),
    ]
    
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='tickets')
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