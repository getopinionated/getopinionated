from django import forms
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from models import Diff

class ProposalForm(forms.Form):
    proposal = forms.CharField(label="",widget=forms.Textarea(attrs={'cols': 80, 'rows': 20}))

    def __init__(self, instance, *args, **kwargs):
        super(ProposalForm, self).__init__(*args, **kwargs)
        self.fulldocument = instance

    def save(self, commit=True):
        pass