from django.forms import widgets
from django.forms.util import flatatt
from django.utils.safestring import mark_safe
from django.utils.datastructures import MultiValueDict, MergeDict
from django.utils.encoding import force_unicode

class TagSelectorWidget(widgets.SelectMultiple):

    class Media:
        css = {
            'all': ('css/chosen.css',)
        }
        js = ('https://ajax.googleapis.com/ajax/libs/jquery/1.6.4/jquery.min.js','js/chosen.jquery.js')

    def render(self, name, selected=None, attrs=None, choices=()):
        if selected is None: selected = []
        final_attrs = self.build_attrs(attrs, name=name)
        output = [u'<select multiple="multiple" class="chosen" %s>' % flatatt(final_attrs)]
        options = self.render_options(choices, selected)
        if options:
            output.append(options)
        output.append('</select>')
        output.append('<script type="text/javascript">$("#%s").chosen();</script>'%attrs['id'])
        return mark_safe(u'\n'.join(output))

    def value_from_datadict(self, data, files, name):
        if isinstance(data, (MultiValueDict, MergeDict)):
            return data.getlist(name)
        return data.get(name, None)

    def _has_changed(self, initial, data):
        if initial is None:
            initial = []
        if data is None:
            data = []
        if len(initial) != len(data):
            return True
        initial_set = set([force_unicode(value) for value in initial])
        data_set = set([force_unicode(value) for value in data])
        return data_set != initial_set
