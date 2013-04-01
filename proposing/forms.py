from django import forms
from common.forms import FocussingModelForm
from common.beautifulsoup import BeautifulSoup
from common import sanitizehtml
from document.models import FullDocument, Diff
from document.widgets import TagSelectorWidget, RichTextEditorWidget
from document.fields import TagChoiceField
from models import VotablePost, UpDownVote, Proposal, Comment, Tag


class ProposalForm(forms.ModelForm):
    title = forms.CharField(widget=forms.TextInput(attrs={'autofocus': 'autofocus'})) # forus on page-load (html5))
    motivation = forms.CharField(widget=forms.Textarea(attrs={'cols': 80, 'rows': 20}))

    def __init__(self, document, *args, **kwargs):
        super(ProposalForm, self).__init__(*args, **kwargs)
        self.document = document
        self.fields["content"] = forms.CharField(widget=RichTextEditorWidget(attrs={'cols': 80, 'rows': 20}), initial=document.content)
        self.fields["tags"] = TagChoiceField(queryset=Tag.objects.all(), widget=TagSelectorWidget())
        self.fields.keyOrder = ['title', 'content', 'motivation','tags', 'proposal_type']

    class Meta:
        model = Proposal
        fields = ('title', 'motivation', 'proposal_type')

    def clean_title(self):
        title = self.cleaned_data["title"]
        if not Proposal().isValidTitle(title):
            raise forms.ValidationError("This title has already been used")
        return title

    def clean_content(self):
        content = self.cleaned_data["content"]
                
        content = sanitizehtml.sanitizeHtml(content)
        content = FullDocument.cleanText(content)
        
        origcont = FullDocument.cleanText(self.document.content)
        if content == origcont:
            raise forms.ValidationError("You should make at least one change")
        return content

    def save(self, user, commit=True):
        ## create diff
        newcontent = FullDocument.cleanText(self.cleaned_data["content"])
        newdiff = Diff.generateDiff(self.document.content, newcontent)
        newdiff.fulldocument = self.document
        newdiff.save()
        
        ## create proposal
        newproposal = super(ProposalForm, self).save(commit=False)
        newproposal.diff = newdiff
        newproposal.creator = creator = user if user.is_authenticated() else None
        newproposal.save()#save before the many-to-manyfield gets created
        for tag in self.cleaned_data["tags"]:
            newproposal.tags.add(tag)
        newproposal.save()
        return newproposal

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('motivation', 'color',)

    def save(self, proposal, user, commit=True):
        new_comment = super(CommentForm, self).save(commit=False)
        new_comment.proposal = proposal
        new_comment.creator = user if user.is_authenticated() else None
        new_comment.save()
        return new_comment
