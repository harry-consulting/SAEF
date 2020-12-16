from django.urls import path
from . import views as user_views
from saef import views as saef_views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('saef/', saef_views.index, name='saef'),
    path('register/', user_views.register, name='register'),
    path('login/', user_views.login, name='login'),
    path('logout/', user_views.logout, name='logout'),
    path('admin/', user_views.admin, name='admin'),
    path('activate/<int:user_id>', user_views.user_activate, name='activate_user'),
    path('deactivate/<int:user_id>',
         user_views.user_deactivate, name='deactivate_user'),

    path('password-reset/', 
         auth_views.PasswordResetView.as_view(
             template_name='users/password_reset.html'), name='password_reset'),
    
    path('password-reset/done/', 
         auth_views.PasswordResetDoneView.as_view(
             template_name='users/password_reset_done.html'), name='password_reset_done'),
    
    path('password-reset-confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='users/password_reset_confirm.html'), name='password_reset_confirm'),
    
    path('password-reset-complete/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='users/password_reset_complete.html'), name='password_reset_complete'),
]
