"""
URL configuration for classbridge project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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
from django.contrib import admin
from django.urls import path,include
from core import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('register/', views.register_student, name='register'),
    path('register/faculty/', views.register_faculty, name='register_faculty'),
    path('', views.home_page, name='home'),
    path('events/', views.event_list, name='event_list'),
    path('events/create/',views.create_event,name='create_event'),
    path('dashboard/',views.dashboard,name='dashboard'),
    path('promote-student/<int:student_id>/', views.promote_to_coordinator, name='promote_to_coordinator'),
    path('events/join/<int:event_id>/', views.join_event, name='join_event'),
    path('events/<int:event_id>/participants/', views.event_participants, name='event_participants'),
    path('events/verify/<int:participation_id>/', views.verify_participation, name='verify_participation'),
    path('events/<int:event_id>/report/', views.email_preview, name='email_preview'),
    path('events/<int:event_id>/download-excel/', views.download_excel_report, name='download_excel_report'),
    path('log-class/', views.log_class, name='log_class'),
    path('events/delete/<int:event_id>/', views.delete_event, name='delete_event'),
    path('log-class/delete/<int:log_id>/', views.delete_class_log, name='delete_class_log'),
    path('profile/delete/', views.delete_account, name='delete_account'),


]
