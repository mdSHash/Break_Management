from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Dashboard for both manager and agent
    path('', views.dashboard, name='dashboard'),

    # Authentication paths
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),
    
    path('dashboard/', views.dashboard, name='dashboard'),
    path('request_break/<int:slot_id>/', views.request_break, name='request_break'),
    path('release_break/<int:slot_id>/', views.release_break, name='release_break'),
    path('assign_break/<int:slot_id>/', views.assign_break, name='assign_break'),
    path('cancel_break/<int:slot_id>/', views.cancel_break, name='cancel_break'),
    
    # Request break slot by agent
    path('request-break/<int:slot_id>/', views.request_break, name='request_break'),

    # Manage break settings (manager only)
    path('manage-settings/', views.manage_settings, name='manage_settings'),

    # Password management views
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='registration/password_reset.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name='password_reset_complete'),
]
