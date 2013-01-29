from django.db import models
from django.utils import timezone
import datetime

import difflib
# Create your models here.

'''
    contains the final version of a certain document, e.g. the manifesto or the program
'''

class Document(models.Model):
    title = models.CharField(max_length=255)
    full_text = models.TextField()
    create_date = models.DateTimeField('Date entered', default=timezone.now())
    version = models.IntegerField()
    
class Diff(models.Model):
    text_representation = models.TextField()
    
    def generateDiff(self, originaltext, derivedtext):
        diff = difflib.ndiff(originaltext.splitlines(1), derivedtext.splitlines(1))
        return Diff(''.join(diff) )
    
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
        