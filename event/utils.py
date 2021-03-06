from django.core.urlresolvers import reverse
from proposing.models import Proposal, Comment, CommentReply

def wrap_html_link_to(target, inner_html):
    """ Wrap inner_html with html code that links to the detail page of target.

    Arguments:
    target -- the model object that is the target of this link
    inner_html -- the HTML code that comes inside the <a>-tags

    """
    return u'<a href="{}">{}</a>'.format(url_to(target), inner_html)

def url_to(target):
    """ Calculate the  url to a relevant detail page of target.

    Arguments:
    target -- the model object that is the target of this url

    """
    if isinstance(target, Proposal):
        return reverse('proposals-detail', args=(target.slug,))
    elif isinstance(target, Comment):
        return u"{}#comment_{}".format(reverse('proposals-detail', args=(target.proposal.slug,)), target.id)
    elif isinstance(target, CommentReply):
        return u"{}#comment_{}".format(reverse('proposals-detail', args=(target.comment.proposal.slug,)), target.comment.id)
    else:
        raise NotImplementedError(u"targets of type {} are not supported.".format(type(target)))

def get_owner_str(votable_post, reading_user, anonymous_alternative='the'):
    """ Return the word that naturally comes before votable_post.human_readable_summary(), in case reading_user
    is reading it.

    Arguments:
    votable_post -- the VotablePost for which this function calculates the owner_str
    reading_user -- the CustomUser that is reading this text
    anonymous_alternative -- if votable_post was posted anonymously, this word will be returned

    """
    # get word that has to come before votable_post
    if reading_user != None and reading_user == votable_post.creator:
        owner_str = 'your'
    elif votable_post.creator == None:
        if anonymous_alternative == 'a' and votable_post.human_readable_summary()[0] in 'aeoi':
            owner_str = 'an' # exception for 'a' when the next line starts with 'a', 'e', 'o' or 'i'
        else:
            owner_str = anonymous_alternative
    else:
        owner_str = u"{}'s".format(votable_post.creator)
    return owner_str

def add_owner(votable_post, reading_user, anonymous_alternative='the'):
    """ Combine get_owner_str() and human_readable_summary(): generate a human-readable string that denotes votable_post together
    with a suitable possessive pronoun.

    Arguments:
    votable_post -- the VotablePost that is displayed to the user in the human-readable text.
    reading_user -- the CustomUser that is reading this text
    anonymous_alternative -- if target_post was posted anonymously, this word will be used as owner_str

    """
    # get word that has to come before origin_post
    owner_str = get_owner_str(votable_post, reading_user, anonymous_alternative)

    # calculate total
    return u"{} {}".format(owner_str, votable_post.human_readable_summary())

def link_and_add_owner(displayed_post, reading_user, target_post=None, anonymous_alternative='the'):
    """ Combine get_owner_str() and wrap_html_link_to(): create a link to target_post with displayed_post as human-readable
    innter text and add an owner_str at the start of this inner text.

    Arguments:
    displayed_post -- the VotablePost that is displayed to the user in the human-readable inner html text.
    reading_user -- the CustomUser that is reading this text
    target_post -- the VotablePost that is the target of this link. If none provided, displayed_post is used.
    anonymous_alternative -- if target_post was posted anonymously, this word will be used as owner_str

    """
    # parse optional target_post
    if target_post == None:
        target_post = displayed_post

    # get word that has to come before origin_post
    owner_str = get_owner_str(displayed_post, reading_user, anonymous_alternative)

    # get link
    link = wrap_html_link_to(target_post, u"{} {}".format(owner_str, displayed_post.human_readable_summary()))
    return link
