from pathlib2 import Path
import pandas as pd
import re

file = Path('../10.1063_1.5004600_fulltext_20190405.txt')
with file.open(encoding='utf-8') as f:
    doc = f.read()

df_sections = pd.read_csv('../10.1063_1.5004600_section_offset_20190405.csv')
df_tags = pd.read_csv('../10.1063_1.5004600_xmltag_offset_20190405.csv')

from collections import namedtuple
from itertools import chain

class my_tokenizer:
    def __init__(self, text):
        self.textList = text

def splitXMLtags(doc):
    tags = df_tags[df_tags.taglist.str.contains('xref|sub|sup|italic')]
    i = 0
    textList = []
    for tag in tags.itertuples():
        s, e = tag.start, tag.end
        #     print(tag.taglist)
        key = ''
        if 'xref' in tag.taglist:
            key = 'REF'
        elif 'subsup' in tag.taglist:
            key = 'SBP'
        elif 'sub' in tag.taglist:
            key = 'SUB'
        elif 'sup' in tag.taglist:
            key = 'SUP'
        elif 'italic' in tag.taglist:
            key = 'ITL'
        if doc[i:s]:
            textList.append({'TX': doc[i:s]})
        textList.append({key: doc[s:e]})
        i = e
    return textList


def splitParagraph(dic):
    textList = []
    text = list(dic.values())[0]
    if re.search('\n', text):
        splitLineSpace = re.finditer(r'([^\n]+)(\n)([^\n]+)?|(\n)', text)
        for s in splitLineSpace:
            for v in s.groups(default=''):
                if v:
                    key = 'TX' if v!='\n' else 'LF'
                    textList += [{key: v}]
    else:
        textList += [dic]
    return textList


def splitBySpace(dic):
    tokenList = []
    text = list(dic.values())[0]
    if re.search(r'\s', text):
        splitspaces = re.finditer(r'(?P<TK>[^\s]+)(?P<SP>\s)?|(?P<SP2>\s)?', text)
        for ss in splitspaces:
            tokenList += [{k: v} for k, v in ss.groupdict(default='').items() if v]
    else:
        tokenList += [{'TK': dic.pop('TX')}]
    return tokenList


def splitByPunct(dic):
    tokenList = []
    text = list(dic.values())[0]
    splitpunct = re.match(r'(?P<TK>[^\,\.\:\;]+)(?P<PN>[\,\.\:\;]$)?', text)
    if splitpunct:
        # print(splitpunct.groupdict(default=''))
        tokenList += [{k: v} for k, v in splitpunct.groupdict(default='').items() if v]
    else:
        tokenList += [dic]
    return tokenList


def splitBlPunct(dic):
    tokenList = []
    text = list(dic.values())[0]
    splitblac = re.match(r'(?P<BR1>^[\(\[])(?P<TK>[^\(\[\)\]]+)(?P<BR2>[\)\]])', text)
    splitblacS = re.match(r'(?P<BR1>^[\(\[])(?P<TK>[^\(\[\)\]]+)', text)
    splitblacE = re.match(r'(?P<TK>[^\(\[\)\]]+)(?P<BR2>[\)\]])', text)
    if splitblac:
        # print(splitblac.groupdict(default=''))
        tokenList += [{k: v} for k, v in splitblac.groupdict(default='').items() if v]
    elif splitblacS:
        tokenList += [{k: v} for k, v in splitblacS.groupdict(default='').items() if v]
    elif splitblacE:
        tokenList += [{k: v} for k, v in splitblacE.groupdict(default='').items() if v]
    else:
        tokenList += [dic]
    return tokenList


def splitInfix(dic):
    tokenList = []
    text = list(dic.values())[0]
    splitinfix = re.match(r'(?P<TK1>[\w]+)?(?P<IN1>[\-\/\u2215])(?P<TK2>[\w]+)(?:(?P<IN2>[\-\/\u2215])(?P<TK3>[\w]+$))?(?:(?P<IN3>[\-\/\u2215])(?P<TK4>[\w]+$))?', text)
    if splitinfix:
        # print(ssplitinfix.groupdict(default=''))
        tokenList += [{k: v} for k, v in splitinfix.groupdict(default='').items() if v]
    else:
        tokenList += [dic]
    return tokenList


textList = splitXMLtags(doc)

paraTextList = []
for dic in textList:
    if ('TX' in dic.keys()):
        paraTextList += splitParagraph(dic)
    else:
        paraTextList += [dic]
b = paraTextList[:]


paraTokenList = []
for dic2 in paraTextList:
    if ('TX' in dic2.keys()):
        paraTokenList += splitBySpace(dic2)
    else:
        paraTokenList += [dic2]


punkTokenList = []
for dic3 in paraTokenList:
    if ('TK' in dic3.keys()):
        punkTokenList += splitByPunct(dic3)
    else:
        punkTokenList += [dic3]


blacTokenList = []
for dic4 in paraTokenList:
    if ('TK' in dic4.keys()):
        blacTokenList += splitBlPunct(dic4)
    else:
        blacTokenList += [dic4]


infixTokenList = []
for dic5 in blacTokenList:
    if ('TK' in dic5.keys()):
        infixTokenList += splitInfix(dic5)
    else:
        infixTokenList += [dic5]


print(infixTokenList )

# a = [''.join(list(t.values())) for t in blacTokenList]
# indexes = [i for i, w in enumerate(a) if w=='\n']
# i = 0
# for index in indexes:
#     s = i; e = index
#     print(''.join(a[s:e]))
#     i = index

# def CalcOffset(List, offset):
#     token_ws = []
#     for i, dic in enumerate(List):
#         if 'SP' in dic.keys():
#             List[i-1].values += dic.values()
#         else:
#             token_ws += [dic]
#