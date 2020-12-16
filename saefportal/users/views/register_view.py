from ..forms import UserRegisterForm
from ..models import UserProfile
from saefportal.settings import EMAIL_HOST_USER, EMAIL_REGISTER_NOTIFY, MSG_EMAIL_USER_REGISTER_SUBJECT, MSG_EMAIL_USER_REGISTER_MSG, MSG_SUCCESS_USER_REGISTER

from django.contrib import messages
from django.core.mail import send_mail
from django.shortcuts import redirect, render

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            new_firstname = form.cleaned_data["firstname"]
            new_lastname = form.cleaned_data["lastname"]
            new_organizations = form.cleaned_data["organization"]
            new_phone = form.cleaned_data["phone"]
            email = form.cleaned_data.get('email')
            UserProfile.objects.create(user=new_user, firstname=new_firstname, lastname=new_lastname, organization=new_organizations, phone=new_phone)
            messages.success(request, MSG_SUCCESS_USER_REGISTER(email))
            if EMAIL_REGISTER_NOTIFY != None:
                send_mail(MSG_EMAIL_USER_REGISTER_SUBJECT(email),
                          MSG_EMAIL_USER_REGISTER_MSG(email, new_phone),
                          EMAIL_HOST_USER,
                          [EMAIL_REGISTER_NOTIFY])
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'register/register.html', {'form': form})