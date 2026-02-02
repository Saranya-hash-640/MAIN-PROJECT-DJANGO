from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, EmployeeProfile, EmployerProfile
from django.utils import timezone
from datetime import timedelta
from .models import EmployeeProfile
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, EmployeeProfile

class EmployeeSignUpForm(UserCreationForm):
    full_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    phone = forms.CharField(
        max_length=15,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    skills = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )
    resume = forms.FileField(
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ('username','email','password1','password2', 'full_name', 'phone', 'skills', 'resume')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'employee'
        user.email = self.cleaned_data.get("email")
        if commit:
            user.save()
            EmployeeProfile.objects.create(
                user=user,
                full_name=self.cleaned_data['full_name'],
                phone=self.cleaned_data['phone'],
                skills=self.cleaned_data['skills'],
                resume=self.cleaned_data.get('resume')
            )
        return user




class EmployerSignUpForm(UserCreationForm):
    company_name = forms.CharField()
    description = forms.CharField(widget=forms.Textarea)

    class Meta:
        model = User
        fields = ('username','email','password1','password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'employer'
        user.email = self.cleaned_data.get("email")
        if commit:
            user.save()
            EmployerProfile.objects.create(
                user=user,
                company_name=self.cleaned_data['company_name'],
                description=self.cleaned_data['description'],
                subscription_end=timezone.now() + timedelta(days=5)
            )
        return user



class ResumeUploadForm(forms.ModelForm):
    class Meta:
        model = EmployeeProfile
        fields = ['resume']  # Make sure 'resume' is the field in your model

# accounts/forms.py
from django import forms
from .models import EmployeeProfile

class EmployeeProfileForm(forms.ModelForm):
    class Meta:
        model = EmployeeProfile
        fields = ('full_name', 'phone', 'skills', 'experience', 'resume')
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'skills': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'experience': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'resume': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
from django import forms
from .models import EmployeeProfile

class EmployeeProfileForm(forms.ModelForm):
    class Meta:
        model = EmployeeProfile
        fields = ['full_name', 'phone', 'skills', 'experience', 'resume']  # Add/remove fields as per your model
