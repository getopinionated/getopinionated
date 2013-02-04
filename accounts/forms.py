from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.forms import AuthenticationForm

import re

class ProfileCreationForm(forms.ModelForm):
    
    """
    A form that creates a user, with no privileges, from the given username and
    password.
    """
    
    #username = forms.RegexField(label=_("Username"), max_length=30, regex=r'^[\w.@+-]+$',
    #    error_messages = {'invalid': _("This value may contain only letters, numbers and @/./+/-/_ characters.")})
    username = forms.RegexField(label=_("Username or emailaddress"), max_length=100,
        regex=r'^[\w.@+-]+$',
        error_messages = {
            'invalid': _("This value may contain only letters, numbers and "
                         "@/./+/-/_ characters.")})
    
    error_messages = {
        'duplicate_username': _("A user with that username already exists."),
        'password_mismatch': _("The two password fields didn't match."),
    }
    
    password1 = forms.CharField(label=_("Password"),
        widget=forms.PasswordInput)
    
    password2 = forms.CharField(label=_("Password confirmation"),
        widget=forms.PasswordInput,
        help_text = _("Enter the same password as above, for verification."))

    class Meta:
        model = User
        fields = ("username", "password1", "password2")

    def clean_username(self):
        # Since User.username is unique, this check is redundant,
        # but it sets a nicer error message than the ORM. See #13147.
        username = self.cleaned_data["username"]
        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            return username
        raise forms.ValidationError(self.error_messages['duplicate_username'])

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1", "")
        password2 = self.cleaned_data["password2"]
        if password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'])
        return password2

    def save(self, commit=True):
        user = super(ProfileCreationForm, self).save(commit=False)
        
        user.set_password(self.cleaned_data["password1"])
        
        if re.match(r'^[a-zA-Z0-9!#$%&*+/=?^_`{|}~-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$', user.username):
            user.email = user.username
            user.username = user.username.split("@", 1)[0] #take the part before the @ in the mail address as username
        else:
            user.email = "no %s"%user.username
        if commit:
            user.save()
        return user

class ProfileUpdateForm(forms.ModelForm):
    username = forms.CharField(label=_("Username"))

    def __init__(self, *args, **kwargs):
        super(forms.ModelForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['readonly'] = True # text input

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email")

    def clean_status(self):
        return self.instance.status

class EmailAuthenticationForm(AuthenticationForm):
    username = forms.CharField(label=_("Email address or username"), max_length=30)