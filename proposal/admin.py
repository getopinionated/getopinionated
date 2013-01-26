from proposal.models import Proposal, Comment
from django.contrib import admin

class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0

class ProposalAdmin(admin.ModelAdmin):
    list_display = ('title','create_date', 'was_published_recently')
    fieldsets = [
                (None, {'fields': ['title','proposal']}),
                ('Dates:', {'fields': ['create_date'], 'classes': ['collapse']}),
            ]
    inlines = [CommentInline]
    list_filter = ['create_date']
    search_fields = ['title', 'proposal']

admin.site.register(Proposal, ProposalAdmin)
