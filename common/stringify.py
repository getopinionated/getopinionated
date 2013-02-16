
ROMAN_TABLE=[('M',1000),('CM',900),('D',500),('CD',400),('C',100),('XC',90),('L',50),('XL',40),('X',10),('IX',9),('V',5),('IV',4),('I',1)]
def int_to_roman(integer):
    parts = []
    for letter, value in ROMAN_TABLE:
        while value <= integer:
            integer -= value
            parts.append(letter)
    return ''.join(parts)

BIG_TABLE=[('G',1000000000),('M',1000000),('k',1000)]
def niceBigInteger(integer):
    for letter, value in BIG_TABLE:
        if integer>=value:
            l = integer*1.0/value
            if l>=100:
                return "%d%s" % (l, letter)
            elif l>=10:
                return "%.1f%s" % (l, letter)
            else:
                return "%.2f%s" % (l, letter)