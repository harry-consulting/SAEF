from django.contrib import messages
from django.contrib.auth import views as auth_views
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import CreateView

from saefportal.settings import EMAIL_REGISTER_NOTIFY
from settings.models import Settings, Contact
from settings.util import send_email_using_settings
from users.forms import UserRegisterForm, LoginAuthForm
from users.models import UserProfile, AdministrativeEvent, OrganizationGroup


class LoginView(SuccessMessageMixin, auth_views.LoginView):
    template_name = "users/authentication/login.html"
    success_message = "Successfully logged in"
    authentication_form = LoginAuthForm

    def get_success_url(self):
        return reverse_lazy("home")


class RegisterView(SuccessMessageMixin, CreateView):
    template_name = "users/authentication/register.html"
    success_url = reverse_lazy("login")
    form_class = UserRegisterForm

    def form_valid(self, form):
        self.object = form.save()
        email = self.object.email

        settings = Settings.objects.get()
        UserProfile.objects.create(user=self.object, first_name=form.cleaned_data["first_name"], settings=settings,
                                   last_name=form.cleaned_data["last_name"], phone=form.cleaned_data["phone"])

        if EMAIL_REGISTER_NOTIFY is not None:
            subject = f"Awaiting register approval for {email}"
            message = f"A new user have been registered and is waiting for approval\nContact information:\nemail - " \
                      f"{email}\nphone - {form.cleaned_data['phone']}\n"

            send_email_using_settings(subject, message, [EMAIL_REGISTER_NOTIFY])

        messages.success(self.request, f"Account created for {email}, please wait for approval.")
        AdministrativeEvent.objects.create(event=f"New user '{self.object}' created", created_by=self.object)

        # Make the new user a contact that can be added to datasets.
        Contact.objects.create(name=f"{form.cleaned_data['first_name']} {form.cleaned_data['last_name']}", email=email)

        # Add the new user to the "All" group.
        self.object.organization_groups.add(OrganizationGroup.objects.get(name="All"))

        return HttpResponseRedirect(self.get_success_url())
