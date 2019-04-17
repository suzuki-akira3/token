from pathlib2 import Path
import pandas as pd
import re

file = Path('./10.1063_1.5004600_fulltext_20190405.txt')
with file.open(encoding='utf-8') as f:
    doc = f.read()

df_sections = pd.read_csv('./10.1063_1.5004600_section_offset_20190405.csv')
df_tags = pd.read_csv('./10.1063_1.5004600_xmltag_offset_20190405.csv')


def rmSections(section):
    secs = df_sections[df_sections['sec_title'].str.match(re.compile(section, re.I))]
    new_doc = doc
    tups = []
    rm_secs = []
    rm_tags = []
    for sec in secs.itertuples():
        s, e = sec.start, sec.end
        tups.append([s, e])
        new_doc = new_doc.replace(doc[s:e], '', 1)

        sloc = df_sections[(df_sections.start >= s) & (df_sections.end <= e)].index
        rm_secs += [i for i in sloc]

        tloc = df_tags[(df_tags.start >= s) & (df_tags.end <= e)].index
        if len(tloc) > 0:
            rm_tags += [i for i in tloc]

    for tup in tups[::-1]:  # subtract from the end of lists
        s, e = tup
        offset = e - s
        df_sections.loc[df_sections.start >= s, 'start'] -= offset
        df_sections.loc[df_sections.end >= e, 'end'] -= offset
        df_tags.loc[df_tags.start >= s, 'start'] -= offset
        df_tags.loc[df_tags.end >= e, 'end'] -= offset

    df_sections.drop(rm_secs)
    df_tags.drop(rm_tags)
    return new_doc


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
    if i < len(doc):
        textList.append({'TX': doc[i:]})
    return textList


def splitParagraph(dic):
    textList = []
    text = list(dic.values())[0]
    if re.search('\n', text):
        splitLineSpace = re.finditer(r'([^\n]+)(\n)([^\n]+)?|(\n)([^\n]+)?', text)
        for s in splitLineSpace:
            for v in s.groups(default=''):
                if v:
                    key = 'TX' if v != '\n' else 'LF'
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
            tokenList += [{k[0:2]: v} for k, v in ss.groupdict(default='').items() if v]
    else:
        tokenList += [{'TK': dic.pop('TX')}]
    return tokenList


def splitByPunct(dic):
    tokenList = []
    text = list(dic.values())[0]
    splitpunct = re.match(r'(?P<TK>.+?)(?P<PN>[,.:;]$)', text)
    if splitpunct:
        #         print(splitpunct.groupdict(default=''))
        tokenList += [{k: v} for k, v in splitpunct.groupdict(default='').items() if v]
    else:
        tokenList += [dic]
    return tokenList


def splitByBlacket(dic):
    tokenList = []
    text = list(dic.values())[0]
    splitblac = re.match(r'(?P<BL1>^[\(\[])(?P<TK>[^\(\[\)\]]+)(?P<BL2>[\)\]])', text)
    splitblacS = re.match(r'(?P<BL1>^[\(\[])(?P<TK>[^\(\[\)\]]+)', text)
    splitblacE = re.match(r'(?P<TK>[^\(\[\)\]]+)(?P<BL2>[\)\]])', text)
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


def splitByInfix(dic):
    tokenList = []
    text = list(dic.values())[0]
    splitinfix = re.match(
        r'(?P<TK1>[\w]+)?(?P<IN1>[\-/\u2215])(?P<TK2>[\w]+)(?:(?P<IN2>[\-/\u2215])(?P<TK3>[\w]+$))?'
        r'(?:(?P<IN3>[\-/\u2215])(?P<TK4>[\w]+$))?',
        text)
    if splitinfix:
        # print(ssplitinfix.groupdict(default=''))
        tokenList += [{k: v} for k, v in splitinfix.groupdict(default='').items() if v]
    else:
        tokenList += [dic]
    return tokenList


section = r'TABLE(.+?)-body'
new_doc = rmSections(section)

textList = splitXMLtags(new_doc)

paraTextList = []
for dic in textList:
    if 'TX' in dic.keys():
        paraTextList += splitParagraph(dic)
    else:
        paraTextList += [dic]

paraTokenList = []
for dic2 in paraTextList:
    if 'TX' in dic2.keys():
        paraTokenList += splitBySpace(dic2)
    else:
        paraTokenList += [dic2]

punkTokenList = []
for dic3 in paraTokenList:
    if 'TK' in dic3.keys():
        punkTokenList += splitByPunct(dic3)
    else:
        punkTokenList += [dic3]

blacTokenList = []
for dic4 in punkTokenList:
    if 'TK' in dic4.keys():
        blacTokenList += splitByBlacket(dic4)
    else:
        blacTokenList += [dic4]

infixTokenList = []
for dic5 in blacTokenList:
    if 'TK' in dic5.keys():
        infixTokenList += splitByInfix(dic5)
    else:
        infixTokenList += [dic5]


def Paragraph(List):
    paragraphTexts = []
    indexes = [i for i, w in enumerate(List) if list(w.values())[0] == '\n']
    s = 0
    for index in indexes:
        e = index + 1
        text = ''.join([''.join(list(w.values())) for w in List[s:e]])
        if text != '\n':
            paragraphTexts.append(text)
        s = e
    return paragraphTexts


def CalcOffset(List, offset):
    entity_dic = {
        'TK': '_',
        'PN': '_',
        'BL1': '_',
        'BL2': '_',
        'LF': '_',
        'SP': '_',
        'TK1': 'compound',
        'TK2': 'compound',
        'TK3': 'compound',
        'TK4': 'compound',
        'IN1': 'compound',
        'IN2': 'compound',
        'IN3': 'compound',
        'SUB': 'subscript',
        'SUP': 'superscript',
        'ITL': 'italic',
        'REF': 'reference',
        '_': '_'
    }
    dic_token = {}
    ipar = 1  # for dic_token.keys()
    itok = 1  # for dic_token.keys()
    ient = 1  # counter for entities
    for i, dic in enumerate(List):
        value = list(List[i].values())[0]
        ent = list(List[i].keys())[0]
        entity = entity_dic.get(ent)
        if entity and entity != '_':
            if entity_dic.get(list(List[i - 1].keys())[0]) != entity_dic.get(
                    ent):  # different entity case from previous
                ient += 1
            entity += f'[{ient}]'

        if i < len(List) - 1 and not 'LF' in List[i].keys() and 'SP' in List[i + 1].keys():
            s = offset
            e = offset + len(value)
            dic_token[ipar, itok] = (s, e, value, entity)  # words without space
            e += len(list(List[i + 1].values())[0])  # count for space
            offset = e
            itok += 1
        elif 'LF' in List[i].keys():
            dic_token[ipar, itok] = value
            offset += len(value)
            ipar += 1
            itok = 1
        elif not 'SP' in List[i].keys():
            s = offset
            e = offset + len(value)
            dic_token[ipar, itok] = (s, e, value, entity)
            offset = e
            itok += 1

    return dic_token


def outputTsv(output, List):
    fw = open(output, 'w', encoding='utf-8')
    tsvText = '#FORMAT=WebAnno TSV 3.2\n'
    tsvText += '#T_SP=webanno.custom.Xml|xml_tag\n\n\n'

    paragraphTexts = Paragraph(List)
    dic_token = CalcOffset(List, offset=0)

    for i, paragraphText in enumerate(paragraphTexts):
        tsvText += (f'#Text={paragraphText}')
        for keys, values in dic_token.items():
            if keys[0] == i + 1:
                if values == '\n':
                    tsvText += values
                else:
                    tsvText += ('{}-{}\t{}-{}\t{}\t{}\t\n'.format(*keys, *values))

    print(tsvText.rstrip('\n\n'), file=fw)


output = './10.1063_1.5004600_webanno.tsv'
outputTsv(output, infixTokenList)
