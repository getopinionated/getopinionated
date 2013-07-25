import re
from urlparse import urljoin
from beautifulsoup import BeautifulSoup, Comment


def sanitizeHtml(value, base_url=None):
    value = value.replace('<div>','').replace('</div>','').replace('<p>','').replace('</p>','').replace('<span>','').replace('</span>','')
    rjs = r'[\s]*(&#x.{1,7})?'.join(list('javascript:'))
    rvb = r'[\s]*(&#x.{1,7})?'.join(list('vbscript:'))
    re_scripts = re.compile('(%s)|(%s)' % (rjs, rvb), re.IGNORECASE)
    validTags = 'br i em strong ul ol li u b a h1 h2 h3 blockquote'.split()
    validAttrs = 'href'.split()
    urlAttrs = 'href src'.split() # Attributes which should have a URL
    soup = BeautifulSoup(value)
    for comment in soup.findAll(text=lambda text: isinstance(text, Comment)):
        # Get rid of comments
        comment.extract()
    for tag in soup.findAll(True):
        if tag.name not in validTags:
            tag.extract()
        attrs = tag.attrs
        tag.attrs = []
        for attr, val in attrs:
            if attr in validAttrs:
                val = re_scripts.sub('', val) # Remove scripts (vbs & js)
                if attr in urlAttrs:
                    val = urljoin(base_url, val) # Calculate the absolute url
                tag.attrs.append((attr, val))

    return soup.renderContents().decode('utf8')