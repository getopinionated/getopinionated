from django import forms
from models import VotablePost, UpDownVote, Proposal, Comment

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('motivation', 'color',)

    def save(self, proposal, user, commit=True):
        new_comment = super(CommentForm, self).save(commit=False)
        new_comment.proposal = proposal
        new_comment.creator = user if user.is_authenticated() else None
        new_comment.save()
        return new_comment
