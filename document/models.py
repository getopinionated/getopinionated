from django.http import Http404
from django.db import models
from django.utils import timezone
from django.db.models import Max
from django.template.defaultfilters import slugify

import difflib

'''
    contains the final version of a certain document, e.g. the manifesto or the program
'''

class FullDocument(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField()
    content = models.TextField() 
    create_date = models.DateTimeField('Date entered', default=timezone.now())
    version = models.IntegerField()
    
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

'''
    contains a diff between two versions of a document. Is the content of a proposal
'''

class Diff(models.Model):
    text_representation = models.TextField()
    fulldocument = models.ForeignKey(FullDocument)
    
    VERYSAFE = 0
    SAFE = 1
    NORMAL = 2
    COMPLIANT = 3
    VERYCOMPLIANT = 4
    
    @staticmethod
    def generateDiff(originaltext, derivedtext):
        originaltext = FullDocument.cleanText(originaltext)
        derivedtext = FullDocument.cleanText(derivedtext)
        diff = difflib.ndiff(originaltext.splitlines(1), derivedtext.splitlines(1))
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
                        pass #TODO
                elif newlines[index].startswith('+ '):
                    if safety == self.VERYSAFE:
                        raise Exception('Conflicting removal with addition (very rare)')
                    else:
                        pass #TODO
                elif newlines[index].startswith('  '):
                    del newlines[index]
            elif diffline.startswith('+ '):
                if newlines[index].startswith('+ '):
                    if safety == self.VERYSAFE:
                        raise Exception('Conflicting addition with another addition')
                    else:
                        pass #TODO
                else:
                    index+=1
                    newlines.insert(index,'  %s'%diffline[2:])
        return Diff(text_representation = ''.join(newlines))   