from django import forms
from models import VotablePost, UpDownVote, Proposal, Comment

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('motivation', 'color',)
