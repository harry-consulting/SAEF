from ..forms import LoginForm

from saefportal.settings import MSG_SUCCESS_USER_LOGIN, MSG_INFO_USER_LOGIN_DEACTIVATED, MSG_ERROR_USER_LOGIN_INCORRECT

from django.contrib.auth import login as django_login, authenticate as django_authenticate
from django.contrib import messages
from django.shortcuts import redirect, render

def login(request):
    if request.method == 'POST':
        form = LoginForm(data = request.POST)
        if form.is_valid():
            user = django_authenticate(email=form.cleaned_data["email"], password=form.cleaned_data["password"])
            if user is not None:
                if user.is_active:
                    django_login(request, user)
                    messages.success(request, MSG_SUCCESS_USER_LOGIN)
                    return redirect('saef')
                else:
                    messages.info(request, MSG_INFO_USER_LOGIN_DEACTIVATED)
            else:
                    messages.error(request, MSG_ERROR_USER_LOGIN_INCORRECT)
    else:
        form = LoginForm()
    return render(request, 'login/login.html', {'form':form,})

