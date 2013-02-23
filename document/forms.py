from django import forms
from models import Diff
from document.models import FullDocument
from proposing.models import Proposal, Tag

class ProposalForm(forms.ModelForm):
    title = forms.CharField(widget=forms.TextInput())
    content = forms.CharField(widget=forms.Textarea(attrs={'cols': 80, 'rows': 20}))
    motivation = forms.CharField(widget=forms.Textarea(attrs={'cols': 80, 'rows': 20}))
    

    def get_my_choices(self):
        return [(tag.name, tag.name) for tag in Tag.objects.all()]

    def __init__(self, *args, **kwargs):
        super(ProposalForm, self).__init__(*args, **kwargs)
        self.fields['tags'] = forms.MultipleChoiceField(required=False, choices=self.get_my_choices(),widget=forms.SelectMultiple(attrs={'data-placeholder':"Choose tags", 'class':"chzn-select", 'multiple':'', 'tabindex':"4"}) )
        self.originalcontent = self.instance.content

    class Meta:
        model = FullDocument
        fields = ("content",)

    def clean_tags(self):
        pass

    def save(self, user, commit=True, tags=[]):
        newcontent = FullDocument.cleanText(self.cleaned_data["content"])
        newdiff = Diff.generateDiff(self.originalcontent,
                                    newcontent)
        newdiff.fulldocument = self.instance
        newdiff.save()
        
        newproposal = Proposal(title = self.cleaned_data["title"],
                               motivation = self.cleaned_data["motivation"],
                               diff = newdiff,
                               creator = user )
        a = self.cleaned_data["tags"]
        a.all()
        newproposal.save()