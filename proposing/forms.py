from django import forms
from common.forms import FocussingModelForm
from common.beautifulsoup import BeautifulSoup
from common import sanitizehtml
from document.models import FullDocument, Diff
from proposing.widgets import TagSelectorWidget, RichTextEditorWidget
from proposing.fields import TagChoiceField, UserChoiceField
from models import VotablePost, UpDownVote, Proposal, Comment, Tag
from django.contrib.auth.models import User
from accounts.models import CustomUser
from django.forms.widgets import SelectMultiple
from django.forms.fields import MultipleChoiceField
from django.forms.models import ModelMultipleChoiceField
from proposing.models import Proxy
import itertools


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
        newproposal.creator = user if user.is_authenticated() else None
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

class ProxyForm(forms.Form):
    
    side_proxy = UserChoiceField(queryset=CustomUser.objects.all())
    side_proxy_tags = TagChoiceField(queryset=Tag.objects.all())
    
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(ProxyForm, self).__init__(*args, **kwargs)        
        proxies = Proxy.objects.all().filter(delegating=user)
        userset = CustomUser.objects.exclude(pk=self.user.pk)
        tagset = Tag.objects.all()
        
        try:
            self.fields['main_proxy'] = UserChoiceField(queryset=userset, widget=TagSelectorWidget(), initial=proxies.get(isdefault=True).delegates.all())
        except:
            self.fields['main_proxy'] = UserChoiceField(queryset=userset, widget=TagSelectorWidget())
        
        count = 0
        self.defaultfields = []
        for proxy in proxies.filter(isdefault=False):
            userfield = UserChoiceField(queryset=userset, widget=TagSelectorWidget(), initial=proxy.delegates.all())
            self.fields["side_proxy%d"%count] = userfield
                        
            tagfield = TagChoiceField(queryset=tagset, widget=TagSelectorWidget(), initial=proxy.tags.all())
            self.fields["side_proxy_tags%d"%count] = tagfield
            self.defaultfields.append(("side_proxy%d"%count,"side_proxy_tags%d"%count))
            count += 1
        
    def getDefaultFieldList(self):
        l = []
        fields = list(self)
        for username,tagname in self.defaultfields:
            userfield = None
            tagfield = None
            for field in fields:
                if field.name == username:
                    userfield = field
                if field.name == tagname:
                    tagfield = field
            if userfield and tagfield:
                l.append((userfield, tagfield))
        return l
    
    def save(self):
        ## create diff
        Proxy.objects.filter(delegating=self.user).delete()
        newproxy = Proxy(delegating=self.user,isdefault=True)
        newproxy.save()
        if 'main_proxy' in self.data.keys():
            for user in self.data.getlist('main_proxy'):
                user_object = CustomUser.objects.get(pk=user)
                newproxy.delegates.add(user_object)
        newproxy.save()
        
        for count in xrange(int(self.data["tagfieldcount"])):
            if "side_proxy%d"%count in self.data.keys() and "side_proxy_tags%d"%count in self.data.keys():
                newproxy = Proxy(delegating=self.user)
                newproxy.save()
                for user in self.data.getlist("side_proxy%d"%count):
                    user_object = CustomUser.objects.get(pk=user)
                    newproxy.delegates.add(user_object)
            
                for tag in self.data.getlist("side_proxy_tags%d"%count):
                    tag_object = Tag.objects.get(pk=tag)
                    newproxy.tags.add(tag_object)
                
                newproxy.save()
        return