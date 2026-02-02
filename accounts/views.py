from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
import razorpay
from .models import Message
from .models import User, EmployeeProfile, EmployerProfile, Payment
from .forms import EmployeeProfileForm
from jobs.models import Job, JobApplication

# Razorpay client
razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

# ----------------- Home -----------------
def home(request):
    return render(request, 'home.html')

# ----------------- Register -----------------
def register(request):
    if request.method == "POST":
        role = request.POST.get('role')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            messages.error(request, "Passwords do not match")
            return redirect('accounts:register')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect('accounts:register')

        user = User.objects.create_user(username=username, email=email, password=password1)
        user.role = role
        user.save()

        if role == 'employee':
            login(request, user)
            return redirect('accounts:create_employee_profile')

        elif role == 'employer':
            EmployerProfile.objects.create(
                user=user,
                company_name=request.POST.get('company_name'),
                description=request.POST.get('description', ''),
                subscription_end=timezone.now() + timedelta(days=5),
                paid=False
            )
            login(request, user)
            return redirect('accounts:payment_page')

        elif role == 'admin':
            user.is_staff = True
            user.is_superuser = True
            user.save()
            login(request, user)
            return redirect('/admin/')

    return render(request, 'accounts/register.html')

# ----------------- Login -----------------
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)

            # Redirect based on role
            role = getattr(user, 'role', None)

            if role == 'employee':
                return redirect('accounts:employee_dashboard')
            elif role == 'employer':
                return redirect('accounts:employer_dashboard')
            elif user.is_staff or user.is_superuser:
                return redirect('/admin/')
            else:
                # Fallback redirect if role not set
                messages.warning(request, "Your account role is not recognized. Redirecting to home.")
                return redirect('home')

        else:
            messages.error(request, "Invalid username or password")

    return render(request, 'accounts/login.html')

# ----------------- Logout -----------------
@login_required
def logout_view(request):
    logout(request)
    return redirect('home')



@login_required
def employee_dashboard(request):
    if request.user.role != 'employee':
        return redirect('dashboard:admin_dashboard')  # or home

    user = request.user
    profile, _ = EmployeeProfile.objects.get_or_create(user=user)
    messages_received = Message.objects.filter(receiver=user).order_by('-timestamp')

    if request.method == 'POST':
        form = EmployeeProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = user
            profile.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('accounts:employee_dashboard')
    else:
        form = EmployeeProfileForm(instance=profile)

    applications = JobApplication.objects.filter(employee=profile).order_by('-applied_at')

    return render(request, 'dashboard/employee_dashboard.html', {
        'profile': profile,
        'form': form,
        'applications': applications,
        'messages_received': messages_received,
    })

# ----------------- Employee Profile (Create/Update) -----------------
@login_required
def create_employee_profile(request):
    if hasattr(request.user, 'employeeprofile'):
        return redirect('accounts:update_employee_profile')

    if request.method == 'POST':
        form = EmployeeProfileForm(request.POST, request.FILES)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            return redirect('accounts:employee_dashboard')
    else:
        form = EmployeeProfileForm()

    return render(request, 'accounts/employee_profile_form.html', {'form': form, 'is_update': False})

@login_required
def update_employee_profile(request):
    profile = get_object_or_404(EmployeeProfile, user=request.user)
    if request.method == 'POST':
        form = EmployeeProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('accounts:employee_dashboard')
    else:
        form = EmployeeProfileForm(instance=profile)

    return render(request, 'accounts/employee_profile_form.html', {'form': form, 'is_update': True})

@login_required
def upload_resume(request):
    profile, _ = EmployeeProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        resume_file = request.FILES.get('resume')
        if resume_file:
            profile.resume = resume_file
            profile.save()
            messages.success(request, "Resume uploaded successfully!")
        else:
            messages.error(request, "Please select a file to upload.")
    return redirect('accounts:employee_dashboard')

# ----------------- Employer Dashboard -----------------
@login_required
def employer_dashboard(request):
    profile = getattr(request.user, 'employerprofile', None)
    jobs_posted = Job.objects.filter(employer=profile) if profile else []
    applications = JobApplication.objects.filter(job__in=jobs_posted)
    return render(request, 'dashboard/employer.html', {
        'profile': profile,
        'jobs': jobs_posted,
        'applications': applications
    })

# ----------------- Payment -----------------
@login_required
def payment_page(request):
    amount_inr = 1000
    amount_paise = amount_inr * 100
    order = razorpay_client.order.create({
        "amount": amount_paise,
        "currency": "INR",
        "payment_capture": 1
    })
    request.session['razorpay_order_id'] = order['id']

    context = {
        "order_id": order['id'],
        "amount_inr": amount_inr,
        "amount_paise": amount_paise,
        "currency": "INR",
        "razorpay_key_id": settings.RAZORPAY_KEY_ID,
    }
    return render(request, "accounts/payment_page.html", context)

@login_required
def payment_success(request):
    if request.method == "POST":
        razorpay_payment_id = request.POST.get("razorpay_payment_id")
        razorpay_order_id = request.POST.get("razorpay_order_id")
        razorpay_signature = request.POST.get("razorpay_signature")
        params_dict = {
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature
        }

        try:
            razorpay_client.utility.verify_payment_signature(params_dict)
            Payment.objects.create(
                user=request.user,
                amount=1000,
                razorpay_payment_id=razorpay_payment_id,
                successful=True
            )
            profile = getattr(request.user, 'employerprofile', None)
            if profile:
                profile.paid = True
                profile.subscription_end = (profile.subscription_end + timedelta(days=30)) if profile.subscription_end else timezone.now() + timedelta(days=30)
                profile.save()
            messages.success(request, "Payment successful! Subscription updated.")
        except razorpay.errors.SignatureVerificationError:
            messages.error(request, "Payment verification failed. Please try again.")

    return redirect('accounts:employer_dashboard')

@login_required
def employee_profile_view(request):
    profile = get_object_or_404(EmployeeProfile, user=request.user)
    return render(request, 'accounts/employee_profile_view.html', {'profile': profile})


@login_required
def send_message(request, employee_id):
    employee = get_object_or_404(User, id=employee_id)
    
    if request.method == "POST":
        content = request.POST.get('content')
        Message.objects.create(sender=request.user, receiver=employee, content=content)
        messages.success(request, "Message sent successfully!")
        return redirect('dashboard:admin_dashboard')  # or employer_dashboard
