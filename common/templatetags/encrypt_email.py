import re
from django import template

register = template.Library()

class EncryptEmail(template.Node):
    def __init__(self, context_var):
        self.context_var = template.Variable(context_var)# context_var
    def render(self, context):
        import random
        email_address = self.context_var.resolve(context)
        character_set = '+-.0123456789@ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz'
        char_list = list(character_set)
        random.shuffle(char_list)
        
        key = ''.join(char_list)
        
        cipher_text = ''
        identifier = 'e' + str(random.randrange(1, 999999999))

        for a in email_address:
            cipher_text += key[ character_set.find(a) ]
            
        script = 'var a="'+key+'";var b=a.split("").sort().join("");var c="'+cipher_text+'";var d="";'
        script += 'for(var e=0;e<c.length;e++)d+=b.charAt(a.indexOf(c.charAt(e)));'
        script += 'document.getElementById("'+identifier+'").innerHTML="<a href=\\"mailto:"+d+"\\">"+d+"</a>"'
        
        
        script = "eval(\""+ script.replace("\\","\\\\").replace('"','\\"') + "\")"
        script = '<script type="text/javascript">/*<![CDATA[*/'+script+'/*]]>*/</script>'
        
        return '<span id="'+ identifier + '">[javascript protected email address]</span>'+ script
        

def  encrypt_email(parser, token):
    """ {% encrypt_email user.email %} """
    tokens = token.contents.split()
    if len(tokens)!=2:
        raise template.TemplateSyntaxError("%r tag accept two argument" % tokens[0])
    return EncryptEmail(tokens[1])

register.tag('encrypt_email', encrypt_email)

