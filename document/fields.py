from django.forms.models import ModelMultipleChoiceField

class TagChoiceField(ModelMultipleChoiceField):
    def label_from_instance(self, tag):
        return "%s" % tag.name