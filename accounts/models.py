from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from datetime import timedelta


class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('employer', 'Employer'),
        ('employee', 'Employee'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='employee')

    def is_admin(self):
        return self.role == 'admin'

    def is_employer(self):
        return self.role == 'employer'

    def is_employee(self):
        return self.role == 'employee'


class EmployeeProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee_profile')
    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    skills = models.TextField()
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)
    experience = models.TextField(blank=True, null=True)  
    qualification = models.CharField(max_length=200, blank=True, null=True)
    profile_pic = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    def __str__(self):
        return self.full_name


class EmployerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employerprofile')
    company_name = models.CharField(max_length=200)
    description = models.TextField()
    paid = models.BooleanField(default=False)
    signup_date = models.DateTimeField(auto_now_add=True)
    subscription_end = models.DateTimeField(null=True, blank=True)

    def is_free_period_active(self):
        return timezone.now() <= self.signup_date + timedelta(days=30)

    def can_post_jobs(self):
        return self.paid or self.is_free_period_active() or (
            self.subscription_end and timezone.now() <= self.subscription_end
        )

    def __str__(self):
        return self.company_name


class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.FloatField()
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    successful = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.sender.username} → {self.receiver.username}"
