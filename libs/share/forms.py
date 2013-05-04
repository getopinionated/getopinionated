from django.forms import *
from django.utils.translation import ugettext_lazy

class EmailForm(forms.Form):
  email_to = EmailField(required=True, label=ugettext_lazy('Send to'))
  email_from = EmailField(required=True, label=ugettext_lazy('Your e-mail address'))
  message = CharField(required=False, label=ugettext_lazy('Your message'))
  next = CharField(required=False, widget=HiddenInput())