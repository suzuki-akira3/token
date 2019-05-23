from pathlib2 import Path
import re
import pandas as pd
from difflib import SequenceMatcher

import splitword

RE_LF = re.compile(r'(?P<TX>[^\n]+)(?P<LF>\n)')


class FileRead:

    def __init__(self, **kwargs):
        self.textfile = kwargs['fdir'] / kwargs['textfile']
        with self.textfile.open(encoding='utf-8') as f:
            self.doc = f.read()
        self.section = kwargs['fdir'] / kwargs['sectionfile']
        self.tag = kwargs['fdir'] / kwargs['tagfile']
        self.df_section = pd.read_csv(self.section)
        self.df_tag = pd.read_csv(self.tag)

    def __repr__(self):
        return self.doc

    def sectionlist(self):
        print(self.df_section)

    def taglist(self):
        print(self.df_tag)

    def rmsections(self, sect):
        secs = self.df_section[self.df_section['sec_title'].str.match(re.compile(sect, re.I))]
        newdoc = self.doc
        tups = []
        rm_secs = []
        rm_tags = []
        for sec in secs.itertuples():
            s, e = sec.span()
            tups.append([s, e])
            newdoc = newdoc.replace(self.doc[s:e], '', 1)

            sloc = self.df_section[(self.df_section.start >= s) & (self.df_section.end <= e)].index
            rm_secs += [i for i in sloc]

            tloc = self.df_tag[(self.df_tag.start >= s) & (self.df_tag.end <= e)].index
            if len(tloc) > 0:
                rm_tags += [i for i in tloc]

        for tup in tups[::-1]:  # subtract from the end of lists
            s, e = tup
            offset = e - s
            self.df_section.loc[self.df_section.start >= s, 'start'] -= offset
            self.df_section.loc[self.df_section.end >= e, 'end'] -= offset
            self.df_tag.loc[self.df_tag.start >= s, 'start'] -= offset
            self.df_tag.loc[self.df_tag.end >= e, 'end'] -= offset

        self.df_section.drop(rm_secs)
        self.df_tag.drop(rm_tags)
        return newdoc

    def newparagraph(self, newdoc):
        return [text.group() for text in RE_LF.finditer(newdoc)]

    def splitxmltags(self, newdoc):
        tags = self.df_tag[self.df_tag.taglist.str.contains('xref|sub|sup|italic')]
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


class OutFile:

    def __init__(self, tokenlist, **kwargs):
        self.tokenlist = tokenlist
        self.outfile = self.section = kwargs['webannotsv']

    def outputtsv(self, orig_paragraph):

        def setparagraph(tokenlist):

            paragraphtexts = []
            indexes = [ii for ii, w in enumerate(tokenlist) if list(w.values())[0] == '\n']
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
                'PR': '_',
                'SR': '_',
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

        fw = open(self.outfile, 'w', encoding='utf-8')
        tsv_text = '#FORMAT=WebAnno TSV 3.2\n'
        tsv_text += '#T_SP=webanno.custom.Xml|xml_tag\n\n\n'

        paragraph_texts = setparagraph(self.tokenlist)
        dic_token = calcoffset(self.tokenlist, offset=0)

        # check paragraphs
        matcher = SequenceMatcher()
        matcher.set_seq1(paragraph_texts)
        matcher.set_seq2(orig_paragraph)
        assert matcher.quick_ratio() == 1, "Paragraphs don't match!"

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
filelist = {
    'fdir': Path('../xml2text'),
    'textfile': '10.1063_1.5004600_fulltext_20190405.txt',
    'sectionfile': '10.1063_1.5004600_section_offset_20190405.csv',
    'tagfile': '10.1063_1.5004600_xmltag_offset_20190405.csv',
    'webannotsv': '10.1063_1.5004600_webanno.tsv'
}

doc = FileRead(**filelist)

import pickle

with open('test.pickle', 'wb') as fw:
    pickle.dump(doc, fw)

section = r'TABLE(.+?)-body'  # remove sections (Table body)
new_doc = doc.rmsections(section)
text_list = doc.splitxmltags(new_doc)

# doc.newparagraph(new_doc)

# tokenize
commands = {
    'splitparagraph': 'TX',
    'splitbyspace': 'TX',
    'splitbypunct2': 'TK',
    'splitbyblacket2': 'TK',
    'splitbyinfix': 'TK',
    'splitbyprefix2': 'TK',
    'splitbysurfix2': 'TK'
}

for command, attr in commands.items():
    newlist = []
    for dic in text_list:
        if attr in dic.keys():
            newlist += eval('splitword.' + command)(dic)
        else:
            newlist += [dic]
        text_list = newlist

# output
out = OutFile(text_list, **filelist)
out.outputtsv(doc.newparagraph(new_doc))
