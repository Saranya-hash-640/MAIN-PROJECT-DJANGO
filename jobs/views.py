from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Job, JobApplication
from .forms import JobForm
from accounts.models import EmployeeProfile
from django.shortcuts import render, get_object_or_404, redirect
from .models import Job, JobApplication
from accounts.models import EmployeeProfile

# Job list
@login_required
def job_list(request):
    jobs = Job.objects.all()
    return render(request, 'jobs/job_list.html', {'jobs': jobs})

# Job detail

# @login_required
# def job_detail(request, job_id):
#     job = get_object_or_404(Job, id=job_id)

#     # Check if current user is an employee
#     profile = getattr(request.user, 'employeeprofile', None)
#     has_applied = False
#     if profile:
#         # Check if this employee has already applied to this job
#         has_applied = JobApplication.objects.filter(job=job, employee=profile).exists()

#     return render(request, 'jobs/job_detail.html', {
#         'job': job,
#         'has_applied': has_applied
#     })
@login_required
def job_detail(request, job_id):
    job = get_object_or_404(Job, id=job_id)

    profile = getattr(request.user, 'employeeprofile', None)
    has_applied = False

    if profile:
        has_applied = JobApplication.objects.filter(
            job=job,
            employee=profile
        ).exists()

    return render(request, 'jobs/job_detail.html', {
        'job': job,
        'has_applied': has_applied,
        'is_employee': profile is not None
    })
# Apply to job
@login_required
def apply_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    profile = getattr(request.user, 'employeeprofile', None)
    
    if profile and request.method == 'POST':
        JobApplication.objects.get_or_create(job=job, employee=profile)
        return redirect('jobs:job_detail', job_id=job.id)
    
    return redirect('jobs:job_detail', job_id=job.id)




# ----------------- Post Job -----------------
@login_required
def post_job(request):
    profile = getattr(request.user, 'employerprofile', None)
    if not profile:
        messages.error(request, "Complete your employer profile first.")
        return redirect('accounts:employer_profile_create')

    if not profile.can_post_jobs():
        messages.error(request, "Subscribe to continue posting jobs.")
        return redirect('accounts:payment_page')

    if request.method == "POST":
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.employer = profile
            job.save()
            messages.success(request, "Job posted successfully!")
            return redirect('accounts:employer_dashboard')
        else:
            messages.error(request, "Please correct errors.")
    else:
        form = JobForm()
    return render(request, 'jobs/post_job.html', {'form': form})

# ----------------- Update Job -----------------
@login_required
def update_job(request, pk):
    job = get_object_or_404(Job, pk=pk, employer=request.user.employerprofile)
    if request.method == 'POST':
        form = JobForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            return redirect('accounts:employer_dashboard')
    else:
        form = JobForm(instance=job)
    return render(request, 'jobs/update_job.html', {'form': form})

# ----------------- Delete Job -----------------
@login_required
def delete_job(request, pk):
    job = get_object_or_404(Job, pk=pk, employer=request.user.employerprofile)
    if request.method == 'POST':
        job.delete()
        return redirect('accounts:employer_dashboard')
    return render(request, 'jobs/confirm_delete.html', {'job': job})


# ----------------- Update Application Status -----------------
@login_required
def update_application_status(request, app_id):
    application = get_object_or_404(JobApplication, id=app_id)
    if application.job.employer != request.user.employerprofile:
        return redirect('accounts:employer_dashboard')

    if request.method == 'POST':
        new_status = request.POST.get('status')
        interview_details = request.POST.get('interview_details', '')
        if new_status in dict(JobApplication.STATUS_CHOICES):
            application.status = new_status
            if new_status == 'Shortlisted':
                application.interview_details = interview_details
                application.message = f"Shortlisted for '{application.job.title}'. Interview: {interview_details}"
            application.save()
    return redirect('job_applications', job_id=application.job.id)

# ----------------- View Employee Profile -----------------

@login_required
def job_applications(request, job_id):
    user = request.user
    job = get_object_or_404(Job, id=job_id)

    # Only the employer who owns this job can view applications
    if hasattr(user, 'employerprofile'):
        if job.employer != user.employerprofile:
            return redirect('accounts:employer_dashboard')
        applications = job.applications.all()
        return render(request, 'jobs/job_applications.html', {
            'job': job,
            'applications': applications
        })
    else:
        # Non-employers (employees) should not access this view
        return redirect('dashboard:employee_dashboard')



@login_required
def view_employee_profile(request, app_id):
    application = get_object_or_404(JobApplication, id=app_id)
    if application.job.employer != request.user.employerprofile:
        return redirect('accounts:employer_dashboard')

    if request.method == 'POST':
        new_status = request.POST.get('status')
        interview_details = request.POST.get('interview_details', '')
        if new_status in dict(JobApplication.STATUS_CHOICES):
            application.status = new_status
            if new_status == 'Shortlisted':
                application.interview_details = interview_details
                application.message = f"Shortlisted for '{application.job.title}'. Interview: {interview_details}"
            application.save()
        return redirect('jobs:job_applications', job_id=application.job.id)

    return render(request, 'jobs/employee_detail.html', {
        'employee': application.employee,
        'application': application,
        'job': application.job,
    })
@login_required
def update_application_status(request, app_id):
    application = get_object_or_404(JobApplication, id=app_id)
    if application.job.employer != request.user.employerprofile:
        return redirect('accounts:employer_dashboard')

    if request.method == 'POST':
        new_status = request.POST.get('status')
        interview_details = request.POST.get('interview_details', '')
        if new_status in dict(JobApplication.STATUS_CHOICES):
            application.status = new_status
            if new_status == 'Shortlisted':
                application.interview_details = interview_details
                application.message = f"Shortlisted for '{application.job.title}'. Interview: {interview_details}"
            application.save()

    return redirect('jobs:job_applications', job_id=application.job.id)
def employee_detail(request, application_id):
    application = get_object_or_404(JobApplication, id=application_id)

    return render(request, 'jobs/employee_detail.html', {
        'employee': application.employee,
        'application': application
    })

@login_required
def delete_job(request, id):
    job = get_object_or_404(Job, id=id)

    if request.method == "POST":
        job.delete()
        return redirect("jobs:job_list")

    return render(request, "jobs/confirm_delete.html", {"job": job})
    
