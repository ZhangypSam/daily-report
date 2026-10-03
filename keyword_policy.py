"""Three concise editorial keywords, shared by private and public checks."""
import re
import unicodedata

def validate_keywords(value):
    if not isinstance(value,list) or len(value)!=3:
        raise ValueError('exactly three keywords required')
    normalized=[]
    for word in value:
        if not isinstance(word,str) or word!=word.strip() or not re.fullmatch(r'[\w .+·/-]{1,16}',word) or not re.search(r'[A-Za-z\u3400-\u9fff]',word):
            raise ValueError('keywords must be concise plain text, 1–16 characters')
        normalized.append(unicodedata.normalize('NFKC',word).casefold())
    if len(set(normalized))!=3:raise ValueError('keywords must be distinct')
    return value
