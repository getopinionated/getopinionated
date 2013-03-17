from django import forms
from django.forms.util import ErrorList

class FocussingModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(FocussingModelForm, self).__init__(*args, **kwargs)
        # focus on first element at page-load (html5)
        print self.fields
        print self.fields.values()[0]
        self.fields.values()[0].widget.attrs.update({'autofocus' : 'autofocus'})

class StarRequiredModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(StarRequiredModelForm, self).__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if field.required:
                field.label = field.label+'*'
