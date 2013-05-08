from django.http import Http404
from django.db import models
from django.utils import timezone
from django.db.models import Max
from django.template.defaultfilters import slugify

from common.stringify import int_to_roman
import difflib


class FullDocument(models.Model):
    """ contains the final version of a certain document, e.g. the manifesto or the program """

    title = models.CharField(max_length=255)
    slug = models.SlugField()
    content = models.TextField() 
    create_date = models.DateTimeField('Date entered', default=timezone.now())
    version = models.IntegerField(default=1)
    
    class Meta:
        unique_together = (("slug", "version"),)

    def save(self, *args, **kwargs):
        if not self.id:
            # Newly created object, so set slug
            self.slug = slugify(self.title)
        super(FullDocument, self).save(*args, **kwargs)

    def applyDiff(self, diff):
        originalText = diff.getOriginalText()
        mytext = FullDocument.cleanText(self.content.__str__())
        if originalText != mytext:
            raise Exception("This diff doesn't apply to this document!")
        newcontent = diff.getNewText()
        newcontent = FullDocument.cleanText(newcontent)
        document = FullDocument(title=self.title, content=diff.getNewText(), create_date=timezone.now(), version=self.version+1)
        document.save()
        return document

    def getFinalVersion(self):
        return self.getFinalVersionFromSlug(self.slug)

    @staticmethod
    def getFinalVersionFromSlug(slug):
        docs_with_slug = FullDocument.objects.filter(slug=slug)
        if docs_with_slug.count() == 0:
            raise Http404('No documents found with this slug ({})'.format(slug))
        v = docs_with_slug.aggregate(Max('version'))
        return docs_with_slug.get(version = v['version__max'])

    def isFinalVersion(self):
        return self.getFinalVersion().version == self.version

    @staticmethod
    def cleanText(text):
        #clean carriages
        text = text.replace('\r\n','\n')
        text = text.replace('\r','\n')
        if not text.endswith('\n'):
            text = text + '\n'
        return text

    @property
    def version_roman(self):
        return int_to_roman(self.version)


class Diff(models.Model):
    """ contains a diff between two versions of a document. Is the content of a proposal """

    text_representation = models.TextField()
    fulldocument = models.ForeignKey(FullDocument)
    
    VERYSAFE = 0
    SAFE = 1
    NORMAL = 2
    COMPLIANT = 3
    VERYCOMPLIANT = 4
    FULLYAUTOMATIC = 5

    def __unicode__(self):
        nchanges = len([l for l in self.text_representation.split('\n') if l.startswith('+') or l.startswith('-')])
        return "Diff for {} with {} changes".format(self.fulldocument.title, nchanges)
    
    @staticmethod
    def generateDiff(originaltext, derivedtext):
        originaltext = FullDocument.cleanText(originaltext)
        derivedtext = FullDocument.cleanText(derivedtext)
        from common.htmldiff import ndiffhtmldiff
        diff = ndiffhtmldiff(originaltext, derivedtext)
        return Diff( text_representation=''.join(diff) )
    
    def getOriginalText(self):
        lines = self.text_representation.__str__().splitlines(1)
        return ''.join([line[2:] for line in lines if line.startswith('- ') or line.startswith('  ')]) 
    
    def getNewText(self):
        lines = self.text_representation.__str__().splitlines(1)
        return ''.join([line[2:] for line in lines if line.startswith('+ ') or line.startswith('  ')])
    
    def getUnifiedDiff(self): #room for optimization
        diff = difflib.unified_diff(self.getOriginalText().splitlines(1), self.getNewText().splitlines(1)) 
        return ''.join(diff) 
    
    def getNDiff(self):
        return self.text_representation
    
    
    
    #TODO: we need a better way to deal with replacements.
    # That is, deletions followed by insertions.
    
    def applyDiffOnThisDiff(self, new_diff, safety=VERYSAFE):
        difflines = new_diff.text_representation.__str__().splitlines(1)
        newlines = self.text_representation.__str__().splitlines(1)
        index = 0
        for diffline in difflines:
            if diffline.startswith('  '):
                while newlines[index][2:]!=diffline[2:]:
                    index+=1
            elif diffline.startswith('- '):
                while newlines[index][2:]!=diffline[2:]:
                    index+=1
                if newlines[index].startswith('- '):
                    if safety == self.VERYSAFE:
                        raise Exception('Conflicting removal')
                    else:
                        #Actually they agree on removing the same line, not a problem
                        pass
                elif newlines[index].startswith('+ '):
                    if safety == self.VERYSAFE:
                        raise Exception('Conflicting removal with addition (very rare)')
                    else:
                        #I want to remove a line, and somebody added it (again?)
                        #Probably I still want to remove it, so remove it
                        del newlines[index]
                elif newlines[index].startswith('  '):
                    del newlines[index]
                else:
                    raise Exception('Bad start of a line in the new diff')
            elif diffline.startswith('+ '):
                if newlines[index].startswith('+ '):
                    if safety == self.VERYSAFE:
                        raise Exception('Conflicting addition with another addition')
                    else:
                        #Actually they agree on adding the same line, not a problem
                        pass
                elif newlines[index].startswith('- '):
                    index+=1
                    newlines.insert(index,'  %s'%diffline[2:])
                elif newlines[index].startswith('  '):
                    index+=1
                    newlines.insert(index,'  %s'%diffline[2:])
                else:
                    raise Exception('Bad start of a line in the new diff')
        return Diff(text_representation = ''.join(newlines))