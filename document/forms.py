from django import forms
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from models import Diff
from document.models import FullDocument

class ProposalForm(forms.ModelForm):
    content = forms.CharField(label="",widget=forms.Textarea(attrs={'cols': 80, 'rows': 20}))

    def __init__(self, *args, **kwargs):
        super(ProposalForm, self).__init__(*args, **kwargs)
        
    class Meta:
        model = FullDocument
        fields = ("content",)

    def save(self, commit=True):
        pass