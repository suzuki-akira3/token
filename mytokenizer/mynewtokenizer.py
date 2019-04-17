from pathlib2 import Path
import pandas as pd
import re


def rmsections(sect):
    secs = df_sections[df_sections['sec_title'].str.match(re.compile(sect, re.I))]
    newdoc = doc
    tups = []
    rm_secs = []
    rm_tags = []
    for sec in secs.itertuples():
        s, e = sec.start, sec.end
        tups.append([s, e])
        newdoc = newdoc.replace(doc[s:e], '', 1)

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
    return newdoc


def splitxmltags(newdoc):
    tags = df_tags[df_tags.taglist.str.contains('xref|sub|sup|italic')]
    i = 0
    textlist = []
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
        if newdoc[i:s]:
            textlist.append({'TX': newdoc[i:s]})
        textlist.append({key: newdoc[s:e]})
        i = e
    if i < len(newdoc):
        textlist.append({'TX': newdoc[i:]})
    return textlist


def splitparagraph(dicpara):
    textlist = []
    text = list(dicpara.values())[0]
    if re.search('\n', text):
        split_line_space = re.finditer(r'([^\n]+)(\n)([^\n]+)?|(\n)([^\n]+)?', text)
        for s in split_line_space:
            for v in s.groups(default=''):
                if v:
                    key = 'TX' if v != '\n' else 'LF'
                    textlist += [{key: v}]
    else:
        textlist += [dicpara]
    return textlist


def splitbyspace(dicsp):
    tokenlist = []
    text = list(dicsp.values())[0]
    if re.search(r'\s', text):
        splitspaces = re.finditer(r'(?P<TK>[^\s]+)(?P<SP>\s)?|(?P<SP2>\s)?', text)
        for ss in splitspaces:
            tokenlist += [{k[0:2]: v} for k, v in ss.groupdict(default='').items() if v]
    else:
        tokenlist += [{'TK': dicsp.pop('TX')}]
    return tokenlist


def splitbypunct(dicpn):
    tokenlist = []
    text = list(dicpn.values())[0]
    splitpunct = re.match(r'(?P<TK>.+?)(?P<PN>[,.:;]$)', text)
    if splitpunct:
        #         print(splitpunct.groupdict(default=''))
        tokenlist += [{k: v} for k, v in splitpunct.groupdict(default='').items() if v]
    else:
        tokenlist += [dicpn]
    return tokenlist


def splitbyblacket(dicbl):
    tokenlist = []
    text = list(dicbl.values())[0]
    splitblac = re.match(r'(?P<BL1>^[\(\[])(?P<TK>[^\(\[\)\]]+)(?P<BL2>[\)\]])', text)
    splitblacS = re.match(r'(?P<BL1>^[\(\[])(?P<TK>[^\(\[\)\]]+)', text)
    splitblacE = re.match(r'(?P<TK>[^\(\[\)\]]+)(?P<BL2>[\)\]])', text)
    if splitblac:
        # print(splitblac.groupdict(default=''))
        tokenlist += [{k: v} for k, v in splitblac.groupdict(default='').items() if v]
    elif splitblacS:
        tokenlist += [{k: v} for k, v in splitblacS.groupdict(default='').items() if v]
    elif splitblacE:
        tokenlist += [{k: v} for k, v in splitblacE.groupdict(default='').items() if v]
    else:
        tokenlist += [dicbl]
    return tokenlist


def splitbyinfix(dicif):
    tokenlist = []
    text = list(dicif.values())[0]
    splitinfix = re.match(
        r'(?P<TK1>[\w]+)?(?P<IN1>[\-/\u2215])(?P<TK2>[\w]+)(?:(?P<IN2>[\-/\u2215])(?P<TK3>[\w]+$))?'
        r'(?:(?P<IN3>[\-/\u2215])(?P<TK4>[\w]+$))?',
        text)
    if splitinfix:
        # print(ssplitinfix.groupdict(default=''))
        tokenlist += [{k: v} for k, v in splitinfix.groupdict(default='').items() if v]
    else:
        tokenlist += [dicif]
    return tokenlist


def setparagraph(tokenlist):
    paragraphtexts = []
    indexes = [i for i, w in enumerate(tokenlist) if list(w.values())[0] == '\n']
    s = 0
    for index in indexes:
        e = index + 1
        text = ''.join([''.join(list(w.values())) for w in tokenlist[s:e]])
        if text != '\n':
            paragraphtexts.append(text)
        s = e
    return paragraphtexts


def calcoffset(tokenlist, offset):
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
    for i in range(len(tokenlist)):
        value = list(tokenlist[i].values())[0]
        ent = list(tokenlist[i].keys())[0]
        entity = entity_dic.get(ent)
        if entity and entity != '_':
            if entity_dic.get(list(tokenlist[i - 1].keys())[0]) != entity_dic.get(
                    ent):  # different entity case from previous
                ient += 1
            entity += f'[{ient}]'

        if i < len(tokenlist) - 1 and 'LF' not in tokenlist[i].keys() and 'SP' in tokenlist[i + 1].keys():
            s = offset
            e = offset + len(value)
            dic_token[ipar, itok] = (s, e, value, entity)  # words without space
            e += len(list(tokenlist[i + 1].values())[0])  # count for space
            offset = e
            itok += 1
        elif 'LF' in tokenlist[i].keys():
            dic_token[ipar, itok] = value
            offset += len(value)
            ipar += 1
            itok = 1
        elif 'SP' not in tokenlist[i].keys():
            s = offset
            e = offset + len(value)
            dic_token[ipar, itok] = (s, e, value, entity)
            offset = e
            itok += 1

    return dic_token


def outputtsv(outfile, tokenlist):
    fw = open(outfile, 'w', encoding='utf-8')
    tsv_text = '#FORMAT=WebAnno TSV 3.2\n'
    tsv_text += '#T_SP=webanno.custom.Xml|xml_tag\n\n\n'

    paragraph_texts = setparagraph(tokenlist)
    dic_token = calcoffset(tokenlist, offset=0)

    for i, paragraph_text in enumerate(paragraph_texts):
        tsv_text += f'#Text={paragraph_text}'
        for keys, values in dic_token.items():
            if keys[0] == i + 1:
                if values == '\n':
                    tsv_text += values
                else:
                    tsv_text += ('{}-{}\t{}-{}\t{}\t{}\t\n'.format(*keys, *values))

    print(tsv_text.rstrip('\n\n'), file=fw)


# main
file = Path('./10.1063_1.5004600_fulltext_20190405.txt')
with file.open(encoding='utf-8') as f:
    doc = f.read()
df_sections = pd.read_csv('./10.1063_1.5004600_section_offset_20190405.csv')
df_tags = pd.read_csv('./10.1063_1.5004600_xmltag_offset_20190405.csv')

section = r'TABLE(.+?)-body'  # remove sections
new_doc = rmsections(section)

text_list = splitxmltags(new_doc)

para_textlist = []
for dic in text_list:
    if 'TX' in dic.keys():
        para_textlist += splitparagraph(dic)
    else:
        para_textlist += [dic]

para_tokenlist = []
for dic_para in para_textlist:
    if 'TX' in dic_para.keys():
        para_tokenlist += splitbyspace(dic_para)
    else:
        para_tokenlist += [dic_para]

punk_tokenlist = []
for dic_pn in para_tokenlist:
    if 'TK' in dic_pn.keys():
        punk_tokenlist += splitbypunct(dic_pn)
    else:
        punk_tokenlist += [dic_pn]

blac_tokenlist = []
for dic_bl in punk_tokenlist:
    if 'TK' in dic_bl.keys():
        blac_tokenlist += splitbyblacket(dic_bl)
    else:
        blac_tokenlist += [dic_bl]

infix_tokenlist = []
for dic_if in blac_tokenlist:
    if 'TK' in dic_if.keys():
        infix_tokenlist += splitbyinfix(dic_if)
    else:
        infix_tokenlist += [dic_if]

output = './10.1063_1.5004600_webanno.tsv'
outputtsv(output, infix_tokenlist)
