import re
from collections import namedtuple

token = namedtuple('token', 'string tag offset')  # 
keytag = namedtuple('key', 'tag attrs')  # 


def add_tag(tag, addtag):  # add tag
    newtag = tag
    if addtag is not None:
        if tag is None:
            newtag = [addtag]
        elif addtag not in tag:
            newtag = tag + [addtag]
    return newtag


def splitbyspace(dic):
    tokenlist = []
    offs, offe = dic.offset 
    s = offs
    text = dic.string
    if re.search(r'\s', text):
        splitspaces = re.finditer(r'(?P<TK>[^\s]+)|(?P<SP>\s)', text)
        for ss in splitspaces:
            if ss.group(1):
                newtag = dic.tag
                e = s + len(ss.group(1))
                tokenlist += [token(ss.group(1), newtag, (s, e))]
                s += len(ss.group(1))
            if ss.group(2):  
                e = s + len(ss.group(2))
                newtag = add_tag(dic.tag, 'SP')
                tokenlist += [token(ss.group(2), newtag, (s, e))]
                s += len(ss.group(2))                       
        assert e == offe, 'Offset is not correct!'
    else:
        tokenlist += [dic]           
    return tokenlist


def splitbypunct(dic):
    tokenlist = []
    offs, offe = dic.offset 
    s = offs    
    text = dic.string
    splitpunct = r'[,.:;]$'
    if re.match(splitpunct, text[-1]):  # and dic.tag is None:
        if len(text) > 1:
            e = s + len(text) - 1
            tokenlist += [token(text[:-1], dic.tag, (s, e))]
            s = e
        e = s + 1
        newtag = add_tag(dic.tag, 'PN')
        tokenlist += [token(text[-1], newtag, (s, e))]
        assert e == offe, 'Offset is not correct!'
    else:
        tokenlist += [dic]
    return tokenlist


def splitbyblacket2(dic):
    tokenlist = []
    offs, offe = dic.offset 
    s = offs  
    text = dic.string
    blacs = '\u0028\u005B\u003C\u2039\u27E8\u3008'  # ( [  #〈  003C(<) 2039(‹) 27E8(⟨) 3008(〈)
    blace = '\u005D\u0029\u003E\u203A\u27E9\u3009'  # ) ]  # 〉 003E(>) 203A(›) 27E9(⟩) 3009(〉)
    blac = blacs + blace

    tx = []
    for i, t in enumerate(text):
        if t in blacs:
#             tokenlist += [{'BL1': t}]
            newtag = add_tag(dic.tag, 'BL1')
            e = s + 1
            tokenlist += [token(t, newtag, (s, e))]
            s = e            
        elif t in blace:
#             tokenlist += [{'BL2': t}]
            newtag = add_tag(dic.tag, 'BL2')
            e = s + 1
            tokenlist += [token(t, newtag, (s, e))]
            s = e  
        else:
            tx += t
            if i < len(text) - 1:
                if text[i + 1] in blac:
#                     tokenlist += [{'TK': ''.join(tx)}]
                    e = s + len(''.join(tx))
                    tokenlist += [token(''.join(tx), dic.tag, (s, e))]
                    s = e  
                    tx = ''
            else:
#                 tokenlist += [{'TK': ''.join(tx)}]
                e = s + len(''.join(tx))
                tokenlist += [token(''.join(tx), dic.tag, (s, e))]
                s = e  
    assert e == offe, 'Offset is not correct!'
    return tokenlist

######################　あとで！
def splitbyinfix(dic):
    tokenlist = []
    offs, offe = dic.offset 
    s = offs
    text = dic.string
#     infix = '\\u002F\\u002D\\u2215\\u2192'  # -/∕ →
#     splitinfix = re.match(
#         rf'(?P<TK1>[^{infix}]+)?(?P<IN1>[{infix}])(?P<TK2>[^{infix}]+)(?:(?P<IN2>[{infix}])(?P<TK3>[^{infix}]+$))?'
#         rf'(?:(?P<IN3>[{infix}])(?P<TK4>[^{infix}]+$))?',
#         text)
#     if splitinfix:
#         #         print(splitinfix.groupdict(default=''))
#         tokenlist += [{k: v} for k, v in splitinfix.groupdict(default='').items() if v]

    infix = '\u002F\u002D\u2215\u2192'  # -/∕ →
    tx = []
    for i, t in enumerate(text):
        if t in infix:
            newtag = add_tag(dic.tag, 'IN')
            s = i
            e = s + 1
            tokenlist += [token(t, newtag, (s, e))]
            
            s = e
        else:
            tx += t
            if i < len(text) - 1:
                if text[i + 1] in infix:
#                     tokenlist += [{'TK': ''.join(tx)}]
                    s = i
                    e = s + len(''.join(tx))
                    tokenlist += [token(''.join(tx), dic.tag, (s, e))]
                    
                    s = e  
                    tx = ''
            else:
                e = s + len(''.join(tx))
                tokenlist += [token(''.join(tx), dic.tag, (s, e))]
                print([token(''.join(tx), dic.tag, (s, e))])
                s = e                      
 
#     assert e == offe, 'Offset is not correct!'
    return tokenlist


def splitbyprefix2(dic):
    tokenlist = []
    offs, offe = dic.offset 
    s = offs  
    text = dic.string
    prefix = r'[\u002B\u002D\u003C-\u003E\u00B1\u2190-\u21FF\u2200-\u22FF]'  # +-=<>±, Arrows, Relations
    if re.match(prefix, text[0]):
#         tokenlist += [{'PR': text[0]}]
        newtag = add_tag(dic.tag, 'PR')
        e = s + 1
        tokenlist += [token(text[0], newtag, (s, e))]
        s = e          
        if len(text) > 1:
#             tokenlist += [{'TK': ''.join(text[1:])}]
            e = s + len(''.join(text[1:]))
            tokenlist += [token(''.join(text[1:]), dic.tag, (s, e))]
            s = e  
        assert e == offe, 'Offset is not correct!'
    else:
        tokenlist += [dic]
    
    return tokenlist


def splitbysurfix2(dic):
    tokenlist = []
    offs, offe = dic.offset 
    s = offs  
    text = dic.string
    surfix = r'[\u0025\u00B0\u002B\u002D\u003C-\u003E\u00B1\u2190-\u21FF\u2200-\u22FF]'  # %,°+-=<>±, Arrows, Relations
    if re.match(surfix, text[-1]):
        if len(text) > 1:
#             tokenlist += [{'TK': ''.join(text[:-1])}]
            e = s + len(''.join(text[:-1]))
            tokenlist += [token(''.join(text[:-1]), dic.tag, (s, e))]
            s = e                                    
#         tokenlist += [{'SR': text[-1]}]
        newtag = add_tag(dic.tag, 'PR')
        e = s + 1
        tokenlist += [token(text[-1], newtag, (s, e))]
        s = e    
        assert e == offe, 'Offset is not correct!' 
    else:
        tokenlist += [dic]
           
    return tokenlist
