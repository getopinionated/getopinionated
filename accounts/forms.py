from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.forms import AuthenticationForm

import re

TABLE=[('M',1000),('CM',900),('D',500),('CD',400),('C',100),('XC',90),('L',50),('XL',40),('X',10),('IX',9),('V',5),('IV',4),('I',1)]
def int_to_roman (integer):
    parts = []
    for letter, value in TABLE:
        while value <= integer:
            integer -= value
            parts.append(letter)
    return ''.join(parts)

class ProfileCreationForm(UserCreationForm):
    
    """
    A form that creates a user, with no privileges, from the given username and
    password.
    """
    
    #username = forms.RegexField(label=_("Username"), max_length=30, regex=r'^[\w.@+-]+$',
    #    error_messages = {'invalid': _("This value may contain only letters, numbers and @/./+/-/_ characters.")})
    username = forms.RegexField(label=_("Username or emailaddress"), max_length=100,
        regex=r'^[\w .@+-]+$',
        error_messages = {
            'invalid': _("This value may contain only letters, numbers and "
                         "@/./+/-/_ characters.")})
    
    error_messages = {
        'duplicate_username': _("A user with that username already exists."),
        'duplicate_email': _("A user with that email address already exists."),
        'password_mismatch': _("The two password fields didn't match."),
    }

    def clean_username(self):
        # Since User.username is unique, this check is redundant,
        # but it sets a nicer error message than the ORM. See #13147.
        username = self.cleaned_data["username"]
        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            try:
                User.objects.get(email=username)
            except User.DoesNotExist:
                return username
            raise forms.ValidationError(self.error_messages['duplicate_email'])
        raise forms.ValidationError(self.error_messages['duplicate_username'])

    def save(self, commit=True):
        user = super(ProfileCreationForm, self).save(commit=False)
        
        user.set_password(self.cleaned_data["password1"])
        # if the username is a mailaddress
        if re.match(r'^[a-zA-Z0-9!#$%&*+/=?^_`{|}~-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$', user.username):
            user.email = user.username
            #extract the username from the mailaddress
            username = user.username.split("@", 1)[0] #take the part before the @ in the mail address as username
            username = username.replace('_',' ')
            username = username.replace('.',' ')
            #if this username would already exist, add roman numbers until this is not the case
            try:
                User.objects.get(username=username)
                #if we get here, the username does already exist
                index = 2
                while True:
                    try:
                        User.objects.get(username="%s %s"%(username,int_to_roman(index)))
                    except User.DoesNotExist:
                        #sweet, we found our username
                        username="%s %s"%(username, int_to_roman(index))
                        break
                    else:
                        index += 1            
            except User.DoesNotExist:
                pass
            user.username = username
        else:
            user.email = ""
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