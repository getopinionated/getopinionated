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
    diff_text = models.TextField()
    
    def generateDiff(self, originaltext, derivedtext):
        diff = difflib.ndiff(originaltext.splitlines(1), derivedtext.splitlines(1))
        return Diff(''.join(diff) )
    
    def getOriginalText(self):
        lines = self.diff_text.splitline(1)
        correct_lines = ''.join(lines)