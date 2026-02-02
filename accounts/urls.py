"""
URL configuration for Aspiro project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Home
    path('', views.home, name='home'),

    # Auth
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Dashboards
    path('employee/dashboard/', views.employee_dashboard, name='employee_dashboard'),
    path('employer/dashboard/', views.employer_dashboard, name='employer_dashboard'),

    # Employee Profile
    path('employee/profile/create/', views.create_employee_profile, name='create_employee_profile'),
    path('employee/profile/update/', views.update_employee_profile, name='update_employee_profile'),
    path('employee/profile/view/', views.employee_profile_view, name='employee_profile_view'),
    path('employee/profile/upload_resume/', views.upload_resume, name='upload_resume'),
    path('employee/upload_resume/', views.upload_resume, name='upload_resume'),
    path('send_message/<int:employee_id>/', views.send_message, name='send_message'),

    # Payment
    path('employer/payment/', views.payment_page, name='payment_page'),
    path('employer/payment/success/', views.payment_success, name='payment_success'),
]
