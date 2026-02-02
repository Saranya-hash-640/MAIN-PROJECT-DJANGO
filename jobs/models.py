from django.db import models
from accounts.models import User

class Job(models.Model):
    # employer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='jobs')
    employer = models.ForeignKey('accounts.EmployerProfile', on_delete=models.CASCADE, related_name='jobs')
    title = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=200)
    salary = models.CharField(max_length=100)
    posted_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title


class JobApplication(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Shortlisted', 'Shortlisted'),
        ('Rejected', 'Rejected'),
        ('Selected','Selected'),
    )
    
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    # employee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applications')
    employee = models.ForeignKey('accounts.EmployeeProfile', on_delete=models.CASCADE, related_name='applications')
    applied_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    interview_details = models.TextField(blank=True, null=True)  # Shortlisting info
    message = models.TextField(blank=True, null=True)  # Shortlist message

    def __str__(self):
        return f"{self.employee.user.username} -> {self.job.title}"
