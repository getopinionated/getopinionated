import re
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.forms import AuthenticationForm
from common.templatetags.filters import slugify

from common.stringify import int_to_roman
from common.forms import FocussingModelForm
from models import CustomUser
import libs.sorl.thumbnail.fields
from libs.sorl.thumbnail.shortcuts import get_thumbnail
from proposing.fields import TagChoiceField
from proposing.models import Proxy, Tag
from proposing.widgets import TagSelectorWidget

error_messages = {
    'duplicate_username': _("A user with that username already exists."),
    'duplicate_email': _("A user with that email address already exists."),
    'password_mismatch': _("The two password fields didn't match."),
}

class CustomUserCreationForm(FocussingModelForm, UserCreationForm):
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
    
    class Meta:
        model = CustomUser
        fields = ("username",)

    def clean_username(self):
        # check if slug is unique (via CustomUser.isValidUserName)
        username = self.cleaned_data["username"]
        if not self.instance.isValidUserName(username):
            raise forms.ValidationError(error_messages['duplicate_username'])
        try:
            CustomUser.objects.get(email=username)
        except CustomUser.DoesNotExist:
            return username
        raise forms.ValidationError(error_messages['duplicate_email'])

    def save(self, commit=True):
        user = super(CustomUserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        # if the username is a mailaddress
        if re.match(r'^[a-zA-Z0-9!#$%&*+/=?^_`{|}~-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$', user.username):
            user.email = user.username
            #extract the username from the mailaddress
            username = user.username.split("@", 1)[0] #take the part before the @ in the mail address as username
            username = username.replace('.','_')
            #if this username would already exist, add roman numbers until this is not the case
            if not user.isValidUserName(username):
                # the username/userslug does already exist
                index = 2
                while True:
                    username="{} {}".format(username, int_to_roman(index))
                    if user.isValidUserName(username):
                        break
                    index += 1
            user.username = username
        else:
            user.email = ""
        if commit:
            user.save()
        return user

class ProfileUpdateForm(forms.ModelForm):
    '''avatar = libs.sorl.thumbnail.fields.ImageField(
        label='Select a file',
        help_text='max. 42 megabytes'
    )'''
    
    def __init__(self, *args, **kwargs):
        super(ProfileUpdateForm, self).__init__(*args, **kwargs)
        self.fields["avatar"].required = False
        # make username readonly (not necessary anymore)
        # self.fields['username'].widget.attrs['readonly'] = True # text input

    class Meta:
        model = CustomUser
        fields = ("username", "first_name", "last_name", "email", "avatar"
                  ,"daily_digest","weekly_digest","send_new","send_voting","send_finished","send_favorites_and_voted")


    def clean_username(self):
        # check if slug is unique (via CustomUser.isValidUserName)
        username = self.cleaned_data["username"]
        if not self.instance.isValidUserName(username):
            raise forms.ValidationError(error_messages['duplicate_username'])
        return username

    def clean_status(self):
        return self.instance.status    

class EmailAuthenticationForm(AuthenticationForm):
    username = forms.CharField(label=_("Email address or username"), max_length=30,
        widget=forms.TextInput(attrs={'autofocus': 'autofocus'})) # forus on page-load (html5)


class SingleProxyForm(forms.Form):
    
    def __init__(self, delegating, delegate, *args, **kwargs):
        self.user = delegating
        self.delegate=delegate
        super(SingleProxyForm, self).__init__(*args, **kwargs)        
        proxies = Proxy.objects.all().filter(delegating__pk__exact=delegating.pk, delegates=delegate, isdefault=False)
        tagset = Tag.objects.all()
        initialtags = Tag.objects.all().filter(pk__in=proxies.values('tags'))
        tagfield = TagChoiceField(queryset=tagset, widget=TagSelectorWidget(), initial=initialtags)
        self.fields["profile_proxy_tags"] = tagfield
        
    def save(self):
        # TODO: remove and create more intelligently, not to fuck up the proxy-form of the delegating
        ## create diff
        ## remove old proxies for this delegate
        proxies = Proxy.objects.filter(delegating=self.user, delegates=self.delegate, isdefault=False)
        for proxy in proxies:
            proxy.delegates.remove(self.delegate)
            if not proxy.delegates.exists():
                proxy.delete()
        
        # create a single new proxy for this delegate
        newproxy = Proxy(delegating=self.user, isdefault=False)
        newproxy.save()
        newproxy.delegates.add(self.delegate)
        if 'profile_proxy_tags' in self.data.keys():
            for tag in self.data.getlist('profile_proxy_tags'):
                tag_object = Tag.objects.get(pk=tag)
                newproxy.tags.add(tag_object)
        newproxy.save()
        return