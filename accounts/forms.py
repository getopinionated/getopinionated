from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import ugettext_lazy as _

class ProfileCreationForm(UserCreationForm):
    username = forms.RegexField(label=_("Username"), max_length=30, regex=r'^[\w.@+-]+$',
        error_messages = {'invalid': _("This value may contain only letters, numbers and @/./+/-/_ characters.")})
    password2 = forms.CharField(label=_("Password confirmation"), widget=forms.PasswordInput,)

    class Meta:
        model = User
        fields = ("username", "password1", "password2")

    def save(self, commit=True):
        user = super(ProfileCreationForm, self).save(commit=False)
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
