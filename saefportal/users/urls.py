from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView
from django.urls import path

from users import views

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('groups/', views.GroupsView.as_view(), name='groups'),
    path('update_groups_permissions/<int:pk>/', views.UserGroupsPermissionsUpdateView.as_view(),
         name='update_groups_permissions'),
    path('resource_access/', views.ResourceAccessView.as_view(), name='resource_access'),
    path('permission_request/<int:pk>/', views.PermissionRequestReadView.as_view(), name='permission_request'),
    path('request_access/', views.PermissionRequestCreateView.as_view(), name='request_access'),
    path('request_access/<str:resource_type>/<int:resource_id>/<int:permission_level>/',
         views.PermissionRequestCreateView.as_view(), name='request_access'),
    path('event_log/', views.EventLogView.as_view(), name='event_log'),
    path('ajax/update_group_structure/', views.update_group_structure, name='update_group_structure'),
    path('ajax/update_tables/', views.update_tables, name='update_tables'),
    path('ajax/toggle_active/', views.toggle_active, name='toggle_active'),
    path('ajax/edit_group_objects/', views.edit_group_objects, name='edit_group_objects'),
    path('ajax/reply_to_request/', views.reply_to_request, name='reply_to_request'),

    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='users/authentication/password/password_reset.html'), name='password_reset'),

    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='users/authentication/password/password_reset_done.html'), name='password_reset_done'),

    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='users/authentication/password/password_reset_confirm.html'), name='password_reset_confirm'),

    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='users/authentication/password/password_reset_complete.html'), name='password_reset_complete'),
]
