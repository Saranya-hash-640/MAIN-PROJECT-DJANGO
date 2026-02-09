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

app_name = 'jobs'

urlpatterns = [
    path('', views.job_list, name='job_list'),

    # Specific paths FIRST
    path('post/', views.post_job, name='post_job'),
    path('application/<int:app_id>/employee/', views.view_employee_profile, name='view_employee_profile'),
    path('application/<int:app_id>/update_status/', views.update_application_status, name='update_application_status'),

    path('<int:job_id>/applications/', views.job_applications, name='job_applications'),
    path('<int:job_id>/apply/', views.apply_job, name='apply_job'),
    path('', views.job_list, name='job_list'),
    

    path('<int:pk>/update/', views.update_job, name='update_job'),
    path('<int:pk>/delete/', views.delete_job, name='delete_job'),

    # MOST GENERIC ALWAYS LAST
    path('<int:job_id>/', views.job_detail, name='job_detail'),
   
   
]
