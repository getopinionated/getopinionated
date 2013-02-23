
import datetime

from django.utils.timezone import is_aware, utc
from django.utils.translation import ugettext, ungettext


ROMAN_TABLE=[('M',1000),('CM',900),('D',500),('CD',400),('C',100),('XC',90),('L',50),('XL',40),('X',10),('IX',9),('V',5),('IV',4),('I',1)]
def int_to_roman(integer):
    parts = []
    for letter, value in ROMAN_TABLE:
        while value <= integer:
            integer -= value
            parts.append(letter)
    return ''.join(parts) if parts else '0'
 
 
"-15k, -10k, -1,5k, -1k, -150, -100, -15, -10, -1, 0, 1, 15, 151, 1k, 1,5k, 1,51k, 10k, 15k, 15,1k, 150k, 151k, 1M, 1,5M, 1,51M"

BIG_TABLE=[('G',1000000000),('M',1000000),('k',1000)]
def niceBigInteger(integer, smallest=False):
    for letter, value in BIG_TABLE:
        if abs(integer)>=value:
            if 10000>integer>=0 and not smallest:
                continue
            s = "%.2f" % (integer*1.0/value)
            s = s[:4]
            if smallest:
                s = s.split(".")[0]
            if s.endswith("0") and "." in s:
                s = s[:-1]
            if s.endswith("0") and "." in s:
                s = s[:-1]
            if s.endswith("."):
                s = s[:-1]
            return s+letter
    #nothing has been found
    return "%d" % integer

def timesince(d, onepart=False):
    """
    Takes two datetime objects and returns the time between d and now
    as a nicely formatted string, e.g. "10 minutes".  If d occurs after now,
    then "0 minutes" is returned.

    Units used are years, months, weeks, days, hours, and minutes.
    Seconds and microseconds are ignored.  Up to two adjacent units will be
    displayed.  For example, "2 weeks, 3 days" and "1 year, 3 months" are
    possible outputs, but "2 weeks, 3 hours" and "1 year, 5 days" are not.

    Adapted from http://blog.natbat.co.uk/archive/2003/Jun/14/time_since
    """
    chunks = (
        (60 * 60 * 24 * 365, lambda n: ungettext('year', 'years', n)),
        (60 * 60 * 24 * 30, lambda n: ungettext('month', 'months', n)),
        (60 * 60 * 24 * 7, lambda n : ungettext('week', 'weeks', n)),
        (60 * 60 * 24, lambda n : ungettext('day', 'days', n)),
        (60 * 60, lambda n: ungettext('hour', 'hours', n)),
        (60, lambda n: ungettext('minute', 'minutes', n))
    )
    # Convert datetime.date to datetime.datetime for comparison.
    if not isinstance(d, datetime.datetime):
        d = datetime.datetime(d.year, d.month, d.day)
    
    now = datetime.datetime.now(utc if is_aware(d) else None)

    delta = now - d
    # ignore microseconds
    since = delta.days * 24 * 60 * 60 + delta.seconds
    past = True
    if since <= 0:
        # d is in the future compared to now, stop processing.
        delta = d - now
        past = False
        
    for i, (seconds, name) in enumerate(chunks):
        count = since // seconds
        if count != 0:
            break
    result = ugettext('%(number)d %(type)s') % {'number': count, 'type': name(count)}
    
    if not onepart:
        if i + 1 < len(chunks):
            # Now get the second item
            seconds2, name2 = chunks[i + 1]
            count2 = (since - (seconds * count)) // seconds2
            if count2 != 0:
                result += ugettext(', %(number)d %(type)s') % {'number': count2, 'type': name2(count2)}
    
    if past:
        result = result + " ago"
    else:
        result = result + " from now"
    return result
