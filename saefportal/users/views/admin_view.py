from saefportal.settings import EMAIL_HOST_USER, MSG_EMAIL_USER_ACTIVATE_SUBJECT, MSG_EMAIL_USER_ACTIVATE_MSG, MSG_SUCCESS_USER_DEACTIVATED, MSG_SUCCESS_USER_ACTIVATED

from ..models import User
from django.shortcuts import redirect, render
from django.contrib import messages
from django.core.mail import send_mail
from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required
def admin(request):
    users_data = User.objects.order_by('-date_joined')
    return render(request, 'admin/admin.html', {'users_data' : users_data})


@staff_member_required()
def user_deactivate(request, user_id):
    user = User.objects.get(pk=user_id)
    user.is_active = False
    user.save()
    messages.success(request, MSG_SUCCESS_USER_DEACTIVATED(user))
    return redirect('admin')

@staff_member_required()
def user_activate(request, user_id):
    user = User.objects.get(pk=user_id)
    user.is_active = True
    user.save()
    send_mail(MSG_EMAIL_USER_ACTIVATE_SUBJECT,
              MSG_EMAIL_USER_ACTIVATE_MSG(user),
              EMAIL_HOST_USER,
              [user.email])
    messages.success(request, MSG_SUCCESS_USER_ACTIVATED(user))
    
    return redirect('admin')
