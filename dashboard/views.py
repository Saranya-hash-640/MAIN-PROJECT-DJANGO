from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Q
from accounts.models import User, EmployeeProfile, EmployerProfile
from accounts.forms import EmployeeProfileForm
from jobs.models import Job, JobApplication
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.utils import timezone
from django.db.models import Count



# -------------------------------------------------
#  1 Dashboard Redirect Based on Role
# -------------------------------------------------
@login_required
def dashboard_redirect(request):
    user = request.user
    # DEBUG: see what Django thinks the role is
    print("Dashboard Redirect -> User:", user.username, "Role:", getattr(user, 'role', None), "is_staff:", user.is_staff)

    if user.is_staff:
        return redirect('dashboard:admin_dashboard')  # Admin users
    elif getattr(user, 'role', '') == 'employer':
        return redirect('accounts:employer_dashboard')  # Employer users
    else:
        return redirect('dashboard:employee_dashboard')  # Default to employee


# -------------------------------------------------
# 2 Admin Dashboard
# -------------------------------------------------
@login_required
def admin_dashboard(request):
    user = request.user
    if not user.is_staff:
        # Only staff/admin can access
        return redirect('accounts:login')

    query = request.GET.get('q', '')

    # Get all employer profiles with related user to reduce queries
    employers = EmployerProfile.objects.select_related('user').all()

    # Apply search filter
    if query:
        employers = employers.filter(
            Q(user__username__icontains=query) |
            Q(user__email__icontains=query) |
            Q(company_name__icontains=query)
        )

    # Annotate additional info
    for emp in employers:
        emp.total_jobs = Job.objects.filter(employer=emp).count()
        emp.paid_status = emp.paid
        emp.days_remaining = (
            max((emp.subscription_end - timezone.now()).days, 0)
            if emp.subscription_end else 0
        )

    context = {
        'employers': employers,
        'query': query,
        'total_jobs_count': Job.objects.count(),
        'total_apps_count': JobApplication.objects.count(),
        'total_employers': employers.count(),
    }

    return render(request, 'dashboard/admin_dashboard.html', context)


#
# -------------------------------------------------
# 3. ADMIN – VIEW EMPLOYER
# -------------------------------------------------

def admin_view_employer(request, employer_id):
    # Get the employer profile
    employer = get_object_or_404(EmployerProfile, id=employer_id)
    
    # Fetch all jobs posted by this employer
    jobs = Job.objects.filter(employer=employer)  # Make sure Job model has 'employer' FK
    # jobs = Job.objects.filter(employer=employer).annotate(total_applications=Count('application'))
    context = {
        'employer': employer,
        'jobs': jobs
    }
    return render(request, 'dashboard/admin_view_employer.html', context)
# -------------------------------------------------
# 4. ADMIN – DELETE EMPLOYER
# -------------------------------------------------
@login_required
def admin_delete_employer(request, employer_id):
    if not (request.user.role == 'admin' or request.user.is_staff):
        return redirect('accounts:login')

    employer = get_object_or_404(EmployerProfile, id=employer_id)
    employer.user.delete()
    employer.delete()

    return redirect('dashboard:admin_dashboard')



# -------------------------------------------------
# 6. EMPLOYEE PROFILE VIEW (SELF)
# -------------------------------------------------
@login_required
def employee_profile_view(request):
    profile = get_object_or_404(EmployeeProfile, user=request.user)
    return render(request, 'dashboard/employee_profile.html', {'profile': profile})


# -------------------------------------------------
# 7. EMPLOYER VIEW EMPLOYEE PROFILE
# -------------------------------------------------
@login_required
def view_employee_profile(request, app_id):
    application = get_object_or_404(JobApplication, id=app_id)

    if application.job.employer != request.user.employerprofile:
        return redirect('accounts:employer_dashboard')

    return render(
        request,
        'dashboard/employee_detail.html',
        {
            'employee': application.employee,
            'application': application
        }
    )

