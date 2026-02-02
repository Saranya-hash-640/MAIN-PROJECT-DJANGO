from django import forms
from .models import Job, JobApplication

# Form for posting a job
class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ['title', 'description', 'location', 'salary']

# Form for applying to a job
class JobApplicationForm(forms.ModelForm):
    class Meta:
        model = JobApplication
        fields = ['job', 'employee']  # Usually employee is set automatically in views
