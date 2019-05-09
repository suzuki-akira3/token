import re


def splitparagraph(dic):
    textlist = []
    text = list(dic.values())[0]
    if re.search('\n', text):
        splitlinefield = re.finditer(r'([^\n]+)(\n)([^\n]+)?|(\n)([^\n]+)?', text)
        for s in splitlinefield:
            for v in s.groups(default=''):
                if v:
                    key = 'TX' if v != '\n' else 'LF'
                    textlist += [{key: v}]
    else:
        textlist += [dic]
    return textlist


def splitbyspace(dic):
    tokenlist = []
    text = list(dic.values())[0]
    if re.search(r'\s', text):
        splitspaces = re.finditer(r'(?P<TK>[^\s]+)(?P<SP>\s)?|(?P<SP2>\s)?', text)
        for ss in splitspaces:
            tokenlist += [{k[0:2]: v} for k, v in ss.groupdict(default='').items() if v]
    else:
        tokenlist += [{'TK': dic.pop('TX')}]
    return tokenlist


def splitbypunct2(dic):
    tokenlist = []
    text = list(dic.values())[0]
    splitpunct = r'[,.:;]$'
    if re.match(splitpunct, text[-1]):
        if len(text) > 1:
            tokenlist += [{'TK': text[:-1]}]
        tokenlist += [{'PN': text[-1]}]
    else:
        tokenlist += [dic]
    return tokenlist


def splitbyblacket2(dic):
    tokenlist = []
    text = list(dic.values())[0]
    blacs = '\u0028\u005B\u003C\u2039\u27E8\u3008'  # ( [  #〈  003C(<) 2039(‹) 27E8(⟨) 3008(〈)
    blace = '\u005D\u0029\u003E\u203A\u27E9\u3009'  # ) ]  # 〉 003E(>) 203A(›) 27E9(⟩) 3009(〉)
    blac = blacs + blace

    index = []
    tx = []
    for i, t in enumerate(text):
        if t in blacs:
            tokenlist += [{'BL1': t}]
            index += [i]
        elif t in blace:
            tokenlist += [{'BL2': t}]
            index += [i]
        else:
            tx += t
            if i < len(text) - 1:
                if text[i + 1] in blac:
                    tokenlist += [{'TK': ''.join(tx)}]
                    tx = ''
            else:
                tokenlist += [{'TK': ''.join(tx)}]
    return tokenlist


def splitbyinfix(dic):
    tokenlist = []
    text = list(dic.values())[0]
    infix = '\\u002F\\u002D\\u2215\\u2192'  # -/∕ →
    splitinfix = re.match(
        rf'(?P<TK1>[^{infix}]+)?(?P<IN1>[{infix}])(?P<TK2>[^{infix}]+)(?:(?P<IN2>[{infix}])(?P<TK3>[^{infix}]+$))?'
        rf'(?:(?P<IN3>[{infix}])(?P<TK4>[^{infix}]+$))?',
        text)
    if splitinfix:
        #         print(splitinfix.groupdict(default=''))
        tokenlist += [{k: v} for k, v in splitinfix.groupdict(default='').items() if v]
    else:
        tokenlist += [dic]
    return tokenlist


def splitbyprefix2(dic):
    tokenlist = []
    text = list(dic.values())[0]
    prefix = r'[\u002B\u002D\u003C-\u003E\u00B1\u2190-\u21FF\u2200-\u22FF]'  # +-=<>±, Arrows, Relations
    if re.match(prefix, text[0]):
        tokenlist += [{'PR': text[0]}]
        if len(text) > 1:
            tokenlist += [{'TK': ''.join(text[1:])}]
    else:
        tokenlist += [{'TK': text}]
    return tokenlist


def splitbysurfix2(dic):
    tokenlist = []
    text = list(dic.values())[0]
    surfix = r'[\u0025\u00B0\u002B\u002D\u003C-\u003E\u00B1\u2190-\u21FF\u2200-\u22FF]'  # %,°+-=<>±, Arrows, Relations
    if re.match(surfix, text[-1]):
        if len(text) > 1:
            tokenlist += [{'TK': ''.join(text[:-1])}]
        tokenlist += [{'SR': text[-1]}]
    else:
        tokenlist += [{'TK': text}]
    return tokenlist
