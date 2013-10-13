from models import FullDocument, Diff
from django.contrib import admin

class FullDocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'create_date', 'version','getTableOfContents',)
    prepopulated_fields = {'slug': ('title',)}

class DiffAdmin(admin.ModelAdmin):
    #fields = ['diff_text', 'getOriginalText', 'getNewText']
    list_display = ('__unicode__', 'text_representation', 'getOriginalText', 'getNewText','getUnifiedDiff')

admin.site.register(FullDocument, FullDocumentAdmin)
admin.site.register(Diff, DiffAdmin)
