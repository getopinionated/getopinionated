from django import forms
from models import Diff
from document.models import FullDocument
from proposing.models import Proposal , Tag
from document.widgets import TagSelectorWidget, RichTextEditorWidget
from document.fields import TagChoiceField
from common.beautifulsoup import BeautifulSoup

class ProposalForm(forms.ModelForm):
    title = forms.CharField(widget=forms.TextInput())
    motivation = forms.CharField(widget=forms.Textarea(attrs={'cols': 80, 'rows': 20}))

    def __init__(self, *args, **kwargs):
        super(ProposalForm, self).__init__(*args, **kwargs)
        self.originalcontent = self.instance.content
        self.fields["content"] = forms.CharField(widget=RichTextEditorWidget(attrs={'cols': 80, 'rows': 20}))
        self.fields["tags"] = TagChoiceField(queryset=Tag.objects.all(), widget=TagSelectorWidget())
        self.fields.keyOrder = ['title', 'content', 'motivation','tags']

    class Meta:
        model = FullDocument
        fields = ("content",)

    def clean_title(self):
        title = self.cleaned_data["title"]
        if not Proposal().isValidTitle(title):
            raise forms.ValidationError("This title has already been used")
        return title

    def clean_content(self):
        content = self.cleaned_data["content"]
        newcont = FullDocument.cleanText(content)
        
        VALID_TAGS = ['strong', 'em', 'br', 'ul', 'ol', 'li', 'h1', 'h2', 'h3', 'blockquote', 'a']
        VALID_ATTRIBUTES = ["href","rel"]
        
        soup = BeautifulSoup(newcont)
        
        #sanitize html received by client
        for tag in soup.findAll(True):
            #remove all unsafe tags (script, form, iframe, media, ...)
            if tag.name not in VALID_TAGS:
                tag.hidden = True
            #remove all unsafe attributes (style, ...)
            remove = []
            map = tag._getAttrMap()
            
            #TODO: there is a bug in the following code, attributes dont get removed
            for attr, val in map.iteritems():
                if attr not in VALID_ATTRIBUTES:
                    #tag.attrs[-index] = 'hillo'
                    remove.append(attr)
                #remove all inline javascript
                elif "javascript" in val:
                    #tag.attrs[-index] = 'hallo'
                    remove.append(attr)
            
            for attr in remove:
                del tag[attr]
            #tag.attrs = [tag.attrs[attr] for i in keep]
    
        newcont = soup.renderContents()
        
        origcont = FullDocument.cleanText(self.originalcontent)
        if newcont == origcont:
            raise forms.ValidationError("You should make at least one change")
        return content

    def save(self, user, commit=True):
        newcontent = FullDocument.cleanText(self.cleaned_data["content"])
        newdiff = Diff.generateDiff(self.originalcontent,
                                    newcontent)
        newdiff.fulldocument = self.instance
        newdiff.save()
        
        newproposal = Proposal(title = self.cleaned_data["title"],
                               motivation = self.cleaned_data["motivation"],
                               diff = newdiff,
                               creator = user if user.is_authenticated() else None)
        newproposal.save()#save before the many-to-manyfield gets created
        for tag in self.cleaned_data["tags"]:
            newproposal.tags.add(tag)
        newproposal.save()
        return newproposal