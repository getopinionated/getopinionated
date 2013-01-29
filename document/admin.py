from models import Document, Diff
from django.contrib import admin

admin.site.register(Document)

class DiffAdmin(admin.ModelAdmin):
    #fields = ['diff_text', 'getOriginalText', 'getNewText']
    list_display = ('text_representation', 'getOriginalText', 'getNewText','getUnifiedDiff')

admin.site.register(Diff, DiffAdmin)