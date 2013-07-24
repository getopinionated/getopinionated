#!/usr/bin/env python
"""
htmldiff.py
Original is (C) Ian Bicking <ianb@colorstudy.com>
With changes from Richard Cyganiak <richard@cyganiak.de>

Finds the differences between two HTML files.  *Not* line-by-line
comparison (more word-by-word).

Command-line usage:
  ./htmldiff.py test1.html test2.html

Better results if you use mxTidy first.  The output is HTML.
"""

from difflib import SequenceMatcher
import re
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO
import cgi

def htmlEncode(s, esc=cgi.escape):
    return esc(s, 1)

commentRE = re.compile('<!--.*?-->', re.S)
tagRE = re.compile('<script.*?>.*?</script>|<.*?>', re.S)
headRE = re.compile('<\s*head\s*>', re.S | re.I)
wsRE = re.compile('^([ \n\r\t]|&nbsp;|<.*?>)+$')
stopwords = ['I', 'a', 'about', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from', 'have', 'how', 'in', 'is', 'it', 'of', 'on', 'or', 'that', 'the', 'this', 'to', 'was', 'what', 'when', 'where', 'who', 'will', 'with']

# Note: Just returning false here gives a generally more accurate,
# but much slower and more noisy result.
def isJunk(x):
#    return False
    return wsRE.match(x) or x.lower() in stopwords

class HTMLMatcher(SequenceMatcher):

    def __init__(self, source1, source2):
        SequenceMatcher.__init__(self, isJunk, source1, source2, False)

    def set_seq1(self, a):
        SequenceMatcher.set_seq1(self, self.splitHTML(a))

    def set_seq2(self, b):
        SequenceMatcher.set_seq2(self, self.splitHTML(b))
        
    def splitTags(self, t):
        result = []
        pos = 0
        while 1:
            match = tagRE.search(t, pos=pos)
            if not match:
                result.append(t[pos:])
                break
            result.append(t[pos:match.start()])
            result.append(match.group(0))
            pos = match.end()
        return result

    #TODO: split on sentences, not words
    def splitWords(self, t):
        #split words by word regex
        #return re.findall(r'([^ \n\r\t,.&;/#=<>()-]+|(?:[ \n\r\t]|&nbsp;)+|[,.&;/#=<>()-])', t)
        #split words by sentence regex
        return re.findall(r'([.;<>()]?[^\n\r\t.;<>()]+[.;<>()]?|(?:[\n\r\t]|&nbsp;)+)', t)

    def splitHTML(self, t):
        t = commentRE.sub('', t)
        r = self.splitTags(t)
        result = []
        for item in r:
            if item.startswith('<'):
                result.append(item)
            else:
                result.extend(self.splitWords(item))
                #result.append(item)
        return result

    def htmlDiff(self, addStylesheet=False):
        opcodes = self.get_opcodes()
        a = self.a
        b = self.b
        out = StringIO()
        for tag, i1, i2, j1, j2 in opcodes:
            if tag == 'equal':
                for item in a[i1:i2]:
                    out.write(item)
            if tag == 'delete':
                self.textDelete(a[i1:i2], out)
            if tag == 'insert':
                self.textInsert(b[j1:j2], out)
            if tag == 'replace':
                if (self.isInvisibleChange(a[i1:i2], b[j1:j2])):
                    for item in b[j1:j2]:
                        out.write(item)
                else:
                    self.textDelete(a[i1:i2], out)
                    self.textInsert(b[j1:j2], out)
        html = out.getvalue()
        out.close()
        if addStylesheet:
            html = self.addStylesheet(html, self.stylesheet())
        return html


    def isVisibleItem(self, item):
        item = re.sub('<[^<]+?>', '', ''.join(item))
        return not not item.strip()
    '''
        Give a context, but also add the previous alinea and the next alinea
    '''
    def htmlContextDiff(self, contextbr = '<br />', addStylesheet=False):
        opcodes = self.get_opcodes()
        a = self.a
        b = self.b
        out = StringIO()
        context = StringIO()
        brsincecontentadded = 0
        added = False
        alreadyadded = False
        for tag, i1, i2, j1, j2 in opcodes:
            if tag == 'equal':
                for item in a[i1:i2]:
                    context.write(item)
                    if contextbr in item:
                        brsincecontentadded += 1
                        if added:
                            if brsincecontentadded>=3:
                                if alreadyadded:
                                    out.write("(...)")
                                out.write(context.getvalue())
                                added = False
                                alreadyadded = True
                                context = StringIO()# #erase first paragraph
                                brsincecontentadded = 0
                        else:
                            if brsincecontentadded>=4:
                                store = context.getvalue()[context.getvalue().find(contextbr)+len(contextbr):]
                                context = StringIO()# #erase first paragraph
                                context.write(store)
                                brsincecontentadded -= 1
            if tag == 'delete':
                self.textDelete(a[i1:i2], context)
                if self.isVisibleItem(a[i1:i2]):
                    brsincecontentadded = 0
                    added = True
            if tag == 'insert':
                self.textInsert(b[j1:j2], context)
                if self.isVisibleItem(b[j1:j2]):
                    brsincecontentadded = 0
                    added = True
            if tag == 'replace':
                brsincecontentadded = 0
                added = True
                if (self.isInvisibleChange(a[i1:i2], b[j1:j2])):
                    for item in b[j1:j2]:
                        context.write(item)
                else:
                    self.textDelete(a[i1:i2], context)
                    self.textInsert(b[j1:j2], context)
        if added:
            if alreadyadded:
                out.write("(...)")
            out.write(context.getvalue())
        html = out.getvalue()
        out.close()
        if addStylesheet:
            html = self.addStylesheet(html, self.stylesheet())
        return html

    def isInvisibleChange(self, seq1, seq2):
        if len(seq1) != len(seq2):
            return False
        for i in range(0, len(seq1)):
            if seq1[i][0] == '<' and seq2[i][0] == '<':
                continue
            if wsRE.match(seq1[i]) and wsRE.match(seq2[i]):
                continue
            if seq1[i] != seq2[i]:
                return False
        return True

    def textDelete(self, lst, out):
        text = ''
        for item in lst:
            if item.startswith('<'):
                self.outDelete(text, out)
                text = ''
                out.write(self.formatDeleteTag(item))
            else:
                text += item
        self.outDelete(text, out)

    def textInsert(self, lst, out):
        text = ''
        for item in lst:
            if item.startswith('<'):
                self.outInsert(text, out)
                text = ''
                out.write(self.formatInsertTag(item))
            else:
                text += item
        self.outInsert(text, out)

    def outDelete(self, s, out):
        if s.strip() == '':
            out.write(s)
        else:
            out.write(self.startDeleteText())
            out.write(s)
            out.write(self.endDeleteText())

    def outInsert(self, s, out):
        if s.strip() == '':
            out.write(s)
        else:
            out.write(self.startInsertText())
            out.write(s)
            out.write(self.endInsertText())

    def stylesheet(self):
        return '''
.insert { background-color: #aaffaa; color: #000!important; }
.delete { background-color: #ff8888; text-decoration: line-through; color: #000!important; }
.tagInsert { background-color: #ccffcc; color: #000!important; }
.tagDelete { background-color: #ffcccc; color: #000!important; }
'''

    def addStylesheet(self, html, ss):
        match = headRE.search(html)
        if match:
            pos = match.end()
        else:
            pos = 0
        return ('%s<style type="text/css">%s</style>%s'
                % (html[:pos], ss, html[pos:]))

    def startInsertText(self):
        return '<span class="insert">'
    def endInsertText(self):
        return '</span>'
    def startDeleteText(self):
        return '<span class="delete">'
    def endDeleteText(self):
        return '</span>'
    
    def formatInsertTag(self, tag):
        if tag.startswith("</"):
            return tag + '</span>'
        if tag.startswith("<br"):
            #return '<span class="tagInsert type1">&para;' + tag + '</span>'
            return '<span class="tagInsert type1">' + tag + '</span>'
        return '<span class="tagInsert">' + tag
            
    def formatDeleteTag(self, tag):
        if tag.startswith("</"):
            return tag+'</span>'
        if tag.startswith("<br"):
            #return '<span class="tagDelete type1">&para;' + tag + '</span>'
            return '<span class="tagDelete type1">' + tag + '</span>'
        return '<span class="tagDelete">'+tag
            

class NoTagHTMLMatcher(HTMLMatcher):
    def formatInsertTag(self, tag):
        return ''
    def formatDeleteTag(self, tag):
        return ''

def htmldiff(source1, source2, addStylesheet=False, contextonly=True):
    """
    Return the difference between two pieces of HTML

        >>> htmldiff('test1', 'test2')
        '<span class="delete">test1 </span> <span class="insert">test2 </span> '
        >>> htmldiff('test1', 'test1')
        'test1 '
        >>> htmldiff('<b>test1</b>', '<i>test1</i>')
        '<span class="tagDelete">delete: <tt>&lt;b&gt;</tt></span> <span class="tagInsert">insert: <tt>&lt;i&gt;</tt></span> <i> test1 <span class="tagDelete">delete: <tt>&lt;/b&gt;</tt></span> <span class="tagInsert">insert: <tt>&lt;/i&gt;</tt></span> </i> '
    """
#    h = HTMLMatcher(source1, source2)
    h = HTMLMatcher(source1, source2)
    if contextonly:
        return h.htmlContextDiff(addStylesheet=addStylesheet)
    else:
        return h.htmlDiff(addStylesheet=addStylesheet)

def diffFiles(f1, f2):
    source1 = open(f1).read()
    source2 = open(f2).read()
    return htmldiff(source1, source2, True)

class SimpleHTMLMatcher(HTMLMatcher):
    """
    Like HTMLMatcher, but returns a simpler diff
    """
    def startInsertText(self):
        return '+['
    def endInsertText(self):
        return ']'
    def startDeleteText(self):
        return '-['
    def endDeleteText(self):
        return ']'
    def formatInsertTag(self, tag):
        return '+[%s]' % tag
    def formatDeleteTag(self, tag):
        return '-[%s]' % tag

def simplehtmldiff(source1, source2):
    """
    Simpler form of htmldiff; mostly for testing, like:

        >>> simplehtmldiff('test1', 'test2')
        '-[test1 ]+[test2 ]'
        >>> simplehtmldiff('<b>Hello world!</b>', '<i>Hello you!</i>')
        '-[<b>]+[<i>]<i> Hello -[world! ]-[</b>]+[you! ]+[</i>]</i> '
    """
    h = SimpleHTMLMatcher(source1, source2)
    return h.htmlDiff()


class NDiffMatcher(HTMLMatcher):
    newline = '\n'
    
    def htmlDiff(self, addStylesheet=False):
        opcodes = self.get_opcodes()
        a = self.a
        b = self.b
        out = StringIO()
        
        for tag, i1, i2, j1, j2 in opcodes:
            if tag == 'equal':
                for item in a[i1:i2]:
                    out.write("  "+item + NDiffMatcher.newline)
            if tag == 'delete':
                self.textDelete(a[i1:i2], out)
            if tag == 'insert':
                self.textInsert(b[j1:j2], out)
            if tag == 'replace':
                if (self.isInvisibleChange(a[i1:i2], b[j1:j2])):
                    for item in b[j1:j2]:
                        out.write("  "+item + NDiffMatcher.newline)
                else:
                    self.textDelete(a[i1:i2], out)
                    self.textInsert(b[j1:j2], out)
        html = out.getvalue()
        out.close()
        return html

    def textDelete(self, lst, out):
        for item in lst:
            out.write("- "+item+NDiffMatcher.newline)
    
    def textInsert(self, lst, out):
        for item in lst:
            out.write("+ "+item+NDiffMatcher.newline)
    

def ndiffhtmldiff(source1, source2):
    """
    Simpler form of htmldiff; used for intern representation
        >>> print ndiffhtmldiff('test1', 'test2')
        - test1
        + test2
    """
    h = NDiffMatcher(source1, source2)
    return h.htmlDiff()

class TextMatcher(HTMLMatcher):


    def set_seq1(self, a):
        SequenceMatcher.set_seq1(self, a.split('\n'))

    def set_seq2(self, b):
        SequenceMatcher.set_seq2(self, b.split('\n'))

    def htmlDiff(self, addStylesheet=False):
        opcodes = self.get_opcodes()
        a = self.a
        b = self.b
        out = StringIO()
        for tag, i1, i2, j1, j2 in opcodes:
            if tag == 'equal':
                self.writeLines(a[i1:i2], out)
            if tag == 'delete' or tag == 'replace':
                out.write(self.startDeleteText())
                self.writeLines(a[i1:i2], out)
                out.write(self.endDeleteText())
            if tag == 'insert' or tag == 'replace':
                out.write(self.startInsertText())
                self.writeLines(b[j1:j2], out)
                out.write(self.endInsertText())
        html = out.getvalue()
        out.close()
        if addStylesheet:
            html = self.addStylesheet(html, self.stylesheet())
        return html

    def writeLines(self, lines, out):
        for line in lines:
            line = htmlEncode(line)
            line = line.replace('  ', '&nbsp; ')
            line = line.replace('\t', '&nbsp; &nbsp; &nbsp; &nbsp; ')
            if line.startswith(' '):
                line = '&nbsp;' + line[1:]
            out.write('<tt>%s</tt><br>\n' % line)

if __name__ == '__main__':
    import sys
    if not sys.argv[1:]:
        print "Usage: %s file1 file2" % sys.argv[0]
        print "or to test: %s test" % sys.argv[0]
    elif sys.argv[1] == 'test' and not sys.argv[2:]:
        import doctest
        doctest.testmod()
    else:
        print diffFiles(sys.argv[1], sys.argv[2])
    