import re
from django import template
from django.utils.safestring import mark_safe
from django.template.defaultfilters import pluralize
from common.stringify import niceBigInteger,timesince
from common.htmldiff import htmldiff

register = template.Library()

@register.filter(name='smallint')
def smallint(value):
    return niceBigInteger(value,smallest=True)

@register.filter(name='mediumint')
def mediumint(value):
    return niceBigInteger(value)

@register.filter(name='humantime')
def humantime(value):
    return timesince(value)

@register.filter(name='shorttime')
def shorttime(value):
    return timesince(value, onepart=True)

@register.filter(name='diffrender',is_safe=True)
def diffrender(diff):
    return mark_safe( #dangerous! Take precautions against XSS
                     htmldiff(diff.getOriginalText(), diff.getNewText(), addStylesheet=True)
                     )

@register.filter(name='fulldiffrender',is_safe=True)
def fulldiffrender(diff):
    return mark_safe( #dangerous! Take precautions against XSS
                     htmldiff(diff.getOriginalText(), diff.getNewText(), addStylesheet=True, contextonly=False)
                     )
    
@register.filter(name='nicejoin')
def nicejoin(l):
    l = list(l) # convert generator to list
    if len(l) <= 1:
        return unicode(l[0]) if l else u""
    else:
        return u"{} and {}".format(", ".join(unicode(e) for e in l[:-1]), l[-1])

@register.filter(name='userjoin')
def userjoin(users, max_num_users=3):
    """ Join the unicode() values of users in a way as illustrated below:
            "user1, user2 and 5 others"

    """
    def _unique_not_none(seq):
        """ filter duplicate entries except if they are None """
        seen = set()
        seen_add = seen.add
        return [x for x in seq if x == None or (x not in seen and not seen_add(x))]
    users = _unique_not_none(users)
    authenticated_users = [u for u in users if u != None]
    if len(authenticated_users) <= max_num_users and users == authenticated_users:
        return nicejoin(users)
    elif not authenticated_users:
        return u"{} user{}".format(len(users), pluralize(len(users)))
    else:
        users_to_show = [unicode(u) for u in authenticated_users[:max_num_users-1]]
        users_left = len(users) - len(users_to_show)
        return u"{} and {} others".format(", ".join(users_to_show), users_left)
    
@register.filter(name='percent')
def percent(f):
    return "%.1f"%(f*100)


@register.filter(name='numberheaders')
def numberheaders(s):
    hcounter = [0,0,0]
    ins = []
    ins.extend([m.start()+3,0] for m in re.finditer('<h1',s))
    ins.extend([m.start()+3,1] for m in re.finditer('<h2',s))
    ins.extend([m.start()+3,2] for m in re.finditer('<h3',s))
    ins = sorted(ins)
    for el in ins:
        hcounter[el[1]]+=1
        el.extend( [hcounter[0], hcounter[1], hcounter[2]] )
        if el[1]==0:
            hcounter[1]=0
            hcounter[2]=0
        elif el[1]==1:
            hcounter[2]=0
    ins.reverse()
    for el in ins:
        if el[1]==0:
            s = s[:el[0]] + ' id="h%s"'%(el[2]) + s[el[0]:]
        elif el[1]==1:
            s = s[:el[0]] + ' id="h%s-%s"'%(el[2],el[3]) + s[el[0]:]
        elif el[1]==2:
            s = s[:el[0]] + ' id="h%s-%s-%s"'%(el[2],el[3],el[4]) + s[el[0]:]
    return s

def slugify(value):
    """
    Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to hyphens.
    """
    import unicodedata
    v=value
    value = unicodedata.normalize('NFKD', unicode(value)).encode('ascii', 'ignore')
    value = unicode(re.sub('[^\w\s-]', '', value).strip().lower())
    value = re.sub('[-\s]+', '-', value)
    value = mark_safe(value)
    if value == '':
        value = mark_safe(''.join([str(ord(c)) for c in v.encode('utf-8')]))
    return value
