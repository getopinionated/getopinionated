from django import forms
from models import Diff
from document.models import FullDocument
from proposing.models import Proposal 

class ProposalForm(forms.ModelForm):
    title = forms.CharField(label="",widget=forms.TextInput())
    content = forms.CharField(label="",widget=forms.Textarea(attrs={'cols': 80, 'rows': 20}))
    motivation = forms.CharField(label="",widget=forms.Textarea(attrs={'cols': 80, 'rows': 20}))

    def __init__(self, *args, **kwargs):
        super(ProposalForm, self).__init__(*args, **kwargs)
        self.originalcontent = self.instance.content

    class Meta:
        model = FullDocument
        fields = ("content",)

    def save(self, user, commit=True):
        newcontent = FullDocument.cleanText(self.cleaned_data["content"])
        newdiff = Diff.generateDiff(self.originalcontent,
                                    newcontent)
        newdiff.fulldocument = self.instance
        newdiff.save()
        
        newproposal = Proposal(title = self.cleaned_data["title"],
                               motivation = self.cleaned_data["motivation"],
                               diff = newdiff,
                               creator = user )
        newproposal.save()