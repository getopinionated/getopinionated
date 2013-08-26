from django import forms
from common.forms import FocussingModelForm
from common.beautifulsoup import BeautifulSoup
from common import sanitizehtml
from document.models import FullDocument, Diff
from proposing.widgets import TagSelectorWidget, RichTextEditorWidget,\
    VeryRichTextEditorWidget, NumberSliderWidget, EmptyTagSelectorWidget
from proposing.fields import TagChoiceField, UserChoiceField
from models import VotablePost, UpDownVote, Proposal, Comment, CommentReply, Tag, VotablePostEdit
from django.contrib.auth.models import User
from accounts.models import CustomUser
from django.forms.widgets import SelectMultiple
from django.forms.fields import MultipleChoiceField
from django.forms.models import ModelMultipleChoiceField
from proposing.models import Proxy
import itertools


class ProposalForm(forms.ModelForm):
    title = forms.CharField(widget=forms.TextInput(attrs={'autofocus': 'autofocus','style':'width: 100%;','placeholder':"Title of the amendment"})) # forus on page-load (html5))
    motivation = forms.CharField(widget=forms.Textarea(attrs={'style':'width: 100%;', 'rows':10,'placeholder':"Your motivation to propose this amendment. Convince the other users that this amendment is a good idea."}))

    def __init__(self, document, *args, **kwargs):
        if 'instance' in kwargs:
            initial = kwargs['instance']
        else:
            initial = None
        super(ProposalForm, self).__init__(*args, **kwargs)
        self.document = document
        
        if initial:
            self.fields["content"] = forms.CharField(widget=RichTextEditorWidget(attrs={'style':'width: 100%;height:100%;'}), initial=initial.diff.getNewText())
            self.fields["discussion_time"] = forms.IntegerField(initial=initial.discussion_time, widget=NumberSliderWidget(attrs={'style':'width: 100%;'}))
            self.fields["tags"] = TagChoiceField(queryset=Tag.objects.all(), initial=initial.tags.all(), widget=TagSelectorWidget(attrs={'style':'width: 100%;', 'data-placeholder':"Tags" }))
        else:
            self.fields["content"] = forms.CharField(widget=RichTextEditorWidget(attrs={'style':'width: 100%;height:100%;'}), initial=document.content)
            self.fields["discussion_time"] = forms.IntegerField(initial=7, widget=NumberSliderWidget(attrs={'style':'width: 100%;'}))
            self.fields["tags"] = TagChoiceField(queryset=Tag.objects.all(), widget=TagSelectorWidget(attrs={'style':'width: 100%;', 'data-placeholder':"Tags" }))
          
        self.fields.keyOrder = ['title', 'content', 'motivation','tags', 'discussion_time']

    class Meta:
        model = Proposal
        fields = ('title', 'motivation')

    def clean_title(self):
        title = self.cleaned_data["title"]
        if not Proposal().isValidTitle(title) and not "edit" in self.data.keys():
            raise forms.ValidationError("This title has already been used")
        return title

    def clean_content(self):
        content = self.cleaned_data["content"]
                
        content = sanitizehtml.sanitizeHtml(content)
        content = FullDocument.cleanText(content)
        origcont = FullDocument.cleanText(self.document.content)
        #Actually, you don't?
        #if content == origcont:
        #    raise forms.ValidationError("You should make at least one change")
        return content

    def save(self, user, commit=True):
        ## create diff
        newcontent = FullDocument.cleanText(self.cleaned_data["content"])
        newdiff = Diff.generateDiff(self.document.content, newcontent)
        newdiff.fulldocument = self.document
        newdiff.save()
        if "edit" in self.data.keys():
            ## edit the proposal
            newproposal = Proposal.objects.get(pk=int(self.data['edit']))
            assert newproposal.isEditableBy(user), "You are not allowed to edit this proposal"
            newproposal.title = self.cleaned_data['title']
            newproposal.motivation = self.cleaned_data['motivation']
        else:
            ## create proposal
            newproposal = super(ProposalForm, self).save(commit=False)
        newproposal.diff = newdiff
        newproposal.creator = user if user.is_authenticated() else None
        newproposal.discussion_time = int(self.cleaned_data["discussion_time"])
        newproposal.save()#save before the many-to-manyfield gets created
        for tag in self.cleaned_data["tags"]:
            newproposal.tags.add(tag)
        newproposal.save()
        ## add VotablePostEdit in case of edit
        if "edit" in self.data.keys():
            VotablePostEdit(user=user, post=newproposal).save()
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

class CommentReplyForm(forms.ModelForm):
    class Meta:
        model = CommentReply
        fields = ('motivation',)

    def save(self, comment, user, commit=True):
        new_comment_reply = super(CommentReplyForm, self).save(commit=False)
        new_comment_reply.comment = comment
        new_comment_reply.creator = user if user.is_authenticated() else None
        new_comment_reply.save()
        return new_comment_reply

class VotablePostEditForm(forms.ModelForm):
    def save(self, user, commit=True):
        votable_post = super(VotablePostEditForm, self).save(commit=commit)
        VotablePostEdit(user=user, post=votable_post).save()
        return votable_post

class CommentEditForm(VotablePostEditForm):
    class Meta:
        model = Comment
        fields = ('motivation', 'color',)

class CommentReplyEditForm(VotablePostEditForm):
    class Meta:
        model = CommentReply
        fields = ('motivation', )

class ProxyForm(forms.Form):
    side_proxy = UserChoiceField(queryset=CustomUser.objects.all(), widget=EmptyTagSelectorWidget(attrs={'data-placeholder':"User, user, ..." }))
    side_proxy_tags = TagChoiceField(queryset=Tag.objects.all(), widget=EmptyTagSelectorWidget(attrs={'data-placeholder':"Tag, tag, ..." }))
    
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