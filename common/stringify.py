
ROMAN_TABLE=[('M',1000),('CM',900),('D',500),('CD',400),('C',100),('XC',90),('L',50),('XL',40),('X',10),('IX',9),('V',5),('IV',4),('I',1)]
def int_to_roman(integer):
    parts = []
    for letter, value in ROMAN_TABLE:
        while value <= integer:
            integer -= value
            parts.append(letter)
    return ''.join(parts)
 
 
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