from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile, User
from django.db.models.signals import post_save
from django.contrib.auth.password_validation import validate_password
from django.core.validators import RegexValidator

class UserRegisterForm(forms.ModelForm):
    email = forms.EmailField(label="Email")
    firstname = forms.CharField(label='First Name', max_length=32)
    lastname = forms.CharField(label='Last Name', max_length=32)
    organization = forms.CharField(label='Organization', max_length=32)
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+4512345678'. Up to 15 digits allowed.")
    phone = forms.CharField(label='Phone Number', max_length=20, validators=[phone_regex])
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput(), validators=[validate_password])
    password2 = forms.CharField(label="Password (again)", widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ['email', 'firstname', 'lastname', 'organization', 'phone', 'password1', 'password2']

    def clean(self):
        cleaned_data = super(UserRegisterForm, self).clean()
        
        if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
            if self.cleaned_data['password1'] != self.cleaned_data['password2']:
                raise forms.ValidationError("Passwords don't match. Please try again!")
        
        if 'email' in self.cleaned_data:
            self.cleaned_data['email'] = self.cleaned_data['email'].lower()
            
        if 'firstname' in self.cleaned_data:
            self.cleaned_data['firstname'] = self.cleaned_data['firstname'].capitalize()
            
        if 'lastname' in self.cleaned_data:
            self.cleaned_data['lastname'] = self.cleaned_data['lastname'].capitalize()
                        
        return self.cleaned_data
    
    def save(self, commit=True):
        user = super(UserRegisterForm, self).save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
            
        return user


class LoginForm(forms.Form): 
    email = forms.EmailField(widget=forms.TextInput(), label='Email')
    password = forms.CharField(widget=forms.PasswordInput(), label='Password')

    class Meta:
        fields = ['email', 'password']
        
    def clean(self):
        cleaned_data = super(LoginForm, self).clean()
            
        if 'email' in self.cleaned_data:
            self.cleaned_data['email'] = self.cleaned_data['email'].lower()

        return self.cleaned_data