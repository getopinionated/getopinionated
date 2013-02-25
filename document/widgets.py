from django.forms import widgets
from django.forms.util import flatatt
from django.utils.safestring import mark_safe
from django.utils.datastructures import MultiValueDict, MergeDict
from django.utils.encoding import force_unicode

class TagSelectorWidget(widgets.SelectMultiple):

    class Media:
        css = {
            'all': ('css/chosen/chosen.css',)
        }
        js = ('js/chosen/chosen.jquery.js',)

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


class RichTextEditorWidget(widgets.Textarea):

    class Media:
        css = {
            'all': ('css/wysihtml5/bootstrap-wysihtml5.css',
                    'css/wysihtml5/bootstrap.min.css')
        }
        js = ('js/wysihtml5/wysihtml5-0.3.0.js',
              'js/wysihtml5/bootstrap.min.js',
              'js/wysihtml5/bootstrap-wysihtml5.js')

    def render(self, name, value, attrs=None):
        final_attrs = self.build_attrs(attrs, name=name)
        output = [u'<textarea class="rich-text-widget" %s>' % flatatt(final_attrs)]
        output.append('%s'%value)
        output.append('</textarea>')
        output.append("""<script type="text/javascript">$('#%s').wysihtml5({
            "font-styles": true,
            "emphasis": true,
            "lists": true,
            "html": false,
            "link": true,
            "image": false,
            "color": false  
        });</script>"""%attrs['id'])
        return mark_safe(u'\n'.join(output))
