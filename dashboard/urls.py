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

app_name = 'dashboard'

urlpatterns = [
    # Redirect based on role
    path('', views.dashboard_redirect, name='dashboard_redirect'),

    # Admin
    path('admin/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/employer/<int:employer_id>/', views.admin_view_employer, name='admin_view_employer'),
    path('admin/employer/<int:employer_id>/delete/', views.admin_delete_employer, name='admin_delete_employer'),
    path('employee/profile/', views.employee_profile_view, name='employee_profile_view'),
    path('employer/employee/<int:app_id>/', views.view_employee_profile, name='view_employee_profile'),
    path('', views.dashboard_redirect, name='dashboard_redirect'),
    # path('employee/', views.employee_dashboard, name='employee_dashboard'),
    path("admin/employer/<int:employer_id>/", views.admin_view_employer,name="admin_view_employer"),


    
]


    
