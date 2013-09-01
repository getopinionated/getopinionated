from django import forms
from common.forms import FocussingModelForm
from common.beautifulsoup import BeautifulSoup
from common import sanitizehtml
from document.models import FullDocument, Diff
from proposing.widgets import TagSelectorWidget, RichTextEditorWidget,\
    VeryRichTextEditorWidget, NumberSliderWidget, EmptyTagSelectorWidget
from proposing.fields import TagChoiceField, UserChoiceField
from django.contrib.auth.models import User
from accounts.models import CustomUser
from django.forms.widgets import SelectMultiple
from django.forms.fields import MultipleChoiceField
from django.forms.models import ModelMultipleChoiceField
from models import VotablePost, UpDownVote, Proposal, AmendmentProposal, PositionProposal, Comment, CommentReply, Tag, VotablePostEdit, Proxy
import itertools

class ProposalForm(forms.ModelForm):
    """ abstract superclass for AmendmentProposalForm and PositionProposalForm """
    is_edit = False
    has_instance = False

    def __init__(self, *args, **kwargs):
        self.has_instance = 'instance' in kwargs and kwargs['instance'] != None
        self.is_edit = kwargs.pop('is_edit') if 'is_edit' in kwargs else self.has_instance
        super(ProposalForm, self).__init__(*args, **kwargs)
        ### add title, content, discussion_time and tags fields
        self.fields["title"] = forms.CharField(widget=forms.TextInput(attrs={'autofocus': 'autofocus','style':'width: 100%;'}))
        self.fields["content"] = forms.CharField(widget=RichTextEditorWidget(attrs={'style':'width: 100%;height:100%;'}),
            initial=self._get_initial_content())
        self.fields["discussion_time"] = forms.IntegerField(widget=NumberSliderWidget(attrs={'style':'width: 100%;'}),
            initial=self.instance.discussion_time if self.has_instance else 7)
        self.fields["tags"] = TagChoiceField(queryset=Tag.objects.all(), widget=TagSelectorWidget(attrs={'style':'width: 100%;', 'data-placeholder':"Tags" }),
            initial=self.instance.tags.all() if self.has_instance else None)
        if self.is_edit:
            self.fields["edit"] = forms.CharField(widget=forms.HiddenInput(), initial=self.instance.pk)

    def _get_initial_content(self):
        raise NotImplementedError()

    def _additional_save_operations(self, proposal):
        return proposal
    
    def clean_content(self):
        content = self.cleaned_data["content"]
        content = sanitizehtml.sanitizeHtml(content)
        content = FullDocument.cleanText(content)
        return content

    def clean_title(self):
        title = self.cleaned_data["title"].strip()
        if not self.instance.isValidTitle(title):
            raise forms.ValidationError("This title has already been used")
        return title

    def save(self, user, commit=True):
        proposal = super(ProposalForm, self).save(commit=False)
        if not self.is_edit:
            proposal.creator = user if user.is_authenticated() else None
        proposal.discussion_time = int(self.cleaned_data["discussion_time"])
        proposal = self._additional_save_operations(proposal)
        assert commit, "can't save form without commit because of many-to-manyfield"
        proposal.save() # save before the many-to-manyfield gets created
        for tag in Tag.objects.all():
            if tag in self.cleaned_data["tags"]:
                proposal.tags.add(tag) # if tag is already added, this has no effect
            elif tag in proposal.tags.all():
                proposal.tags.remove(tag)
        proposal.save()
        ## add VotablePostEdit in case of edit
        if self.is_edit:
            VotablePostEdit(user=user, post=proposal).save()
        return proposal

class AmendmentProposalForm(ProposalForm):
    motivation = forms.CharField(widget=forms.Textarea(attrs={'style':'width: 100%;', 'rows':10,'placeholder':"Your motivation to propose this amendment. Convince the other users that this amendment is a good idea."}))

    def __init__(self, document, *args, **kwargs):
        self.document = document
        super(AmendmentProposalForm, self).__init__(*args, **kwargs)
        ## add placeholders for shared fields
        self.fields['title'].widget.attrs['placeholder'] = "Title of the amendment"

    class Meta:
        model = AmendmentProposal
        fields = ('title', 'motivation',)

    def _get_initial_content(self):
        return self.instance.diff.getNewText() if self.has_instance else self.document.content

    def clean_content(self):
        content = super(AmendmentProposalForm, self).clean_content()
        ## check if content has changed w.r.t. original document
        ## for an unknown reason Jonas removed this
        #origcont = FullDocument.cleanText(self.document.content)
        #if content == origcont:
        #   raise forms.ValidationError("You should make at least one change")
        return content

    def _additional_save_operations(self, amendmentproposal):
        ## create diff
        content = FullDocument.cleanText(self.cleaned_data["content"])
        newdiff = Diff.generateDiff(self.document.content, content)
        newdiff.fulldocument = self.document
        newdiff.save()
        ## add diff to amendmentproposal
        amendmentproposal.diff = newdiff
        return amendmentproposal

class PositionProposalForm(ProposalForm, FocussingModelForm):
    def __init__(self, *args, **kwargs):
        super(PositionProposalForm, self).__init__(*args, **kwargs)
        ## add placeholders for shared fields
        self.fields['title'].widget.attrs['placeholder'] = "State the position concicely"
        self.fields['content'].widget.attrs['placeholder'] = "<b>Position:</b><br>[Optional] Clarification of position stated above<br><br><b>Motivation:</b><br>..."
        ## modify titles for shared fields
        self.fields['title'].label = ""
        self.fields['tags'].label = ""
        self.fields['content'].label = "Position and motivation"

    class Meta:
        model = PositionProposal
        fields = ('title', 'tags', 'discussion_time')

    def _get_initial_content(self):
        return self.instance.position_text

    def _additional_save_operations(self, positionproposal):
        ## add position_text to positionproposal
        positionproposal.position_text = self.cleaned_data["content"]
        return positionproposal

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