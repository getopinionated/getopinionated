from django.db import models
from django.utils import timezone

import difflib

'''
    contains the final version of a certain document, e.g. the manifesto or the program
'''

class FullDocument(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField() 
    create_date = models.DateTimeField('Date entered', default=timezone.now())
    version = models.IntegerField()
    
    def applyDiff(self, diff):
        originalText = diff.getOriginalText()
        if originalText != self.content.__str__():
            raise Exception("This diff doesn't apply to this document!")
        return FullDocument(title=self.title, content=diff.getOriginalText(), create_date=timezone.now(), version=self.version+1)

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