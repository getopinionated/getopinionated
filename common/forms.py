from django import forms
from django.forms.util import ErrorList

class CustomModelForm(forms.ModelForm):
    def __init__(self, data=None, files=None, auto_id='id_%s', prefix=None,
                 initial=None, error_class=ErrorList, label_suffix=':',
                 empty_permitted=False, instance=None):
        super(CustomModelForm, self).__init__(data, files, auto_id, prefix, initial,
                                            error_class, label_suffix, empty_permitted, instance)
        for name, field in self.fields.items():
            if field.required:
                field.label = field.label+'*'
