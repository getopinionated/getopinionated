from django.core.urlresolvers import reverse
from proposing.models import Proposal, Comment, CommentReply

def link_to(target, inner_html):
    """ wraps inner_html with html code that links to the detail page of target. """
    ## get url
    url = ""
    if isinstance(target, Proposal):
        url = reverse('proposals-detail', args=(target.slug,))
    elif isinstance(target, Comment):
        url = u"{}#comment_{}".format(reverse('proposals-detail', args=(target.proposal.slug,)), target.id)
    elif isinstance(target, CommentReply):
        url = u"{}#comment_{}".format(reverse('proposals-detail', args=(target.comment.proposal.slug,)), target.comment.id)
    else:
        raise NotImplementedError(u"targets of type {} are not supported.".format(type(target)))

    ## wrap inner_html
    return u'<a href="{}">{}</a>'.format(url, inner_html)
