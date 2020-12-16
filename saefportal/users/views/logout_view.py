from saefportal.settings import MSG_SUCCESS_USER_LOGOUT

from django.contrib.auth import logout as django_logout
from django.contrib import messages
from django.shortcuts import redirect

def logout(request):
    django_logout(request)
    messages.success(request, MSG_SUCCESS_USER_LOGOUT)
    return redirect('login')