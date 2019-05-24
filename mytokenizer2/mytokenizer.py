from pathlib2 import Path
import re
import pandas as pd

from collections import namedtuple

token = namedtuple('token', 'string tag offset')  # type(elem): string, type(tags): list
keytag = namedtuple('key', 'tag attrs')  # type(elem): string, type(tags): list


class ReadFile:

    def __init__(self, **kwargs):
        self.textfile = kwargs['textfile']
        with self.textfile.open(encoding='utf-8') as f:
            self.doc = f.read()

        self.section = kwargs['sectionfile']
        self.df_section = pd.read_csv(self.section)

        self.tag = kwargs['tagfile']
        self.df_tag = pd.read_csv(self.tag)

    def __repr__(self):
        return self.doc

    @property
    def text(self):
        return self.doc

    @property
    def sectionlist(self):
        return self.df_section

    @property
    def taglist(self):
        return self.df_tag

    def offset(self, s, e):
        return self.doc[s:e]

    def rmsections(self, sect):
        secs = self.df_section[self.df_section['sec_title'].str.match(sect)]
        newdoc = self.doc
        tups = []
        rm_secs = []
        rm_tags = []

        for sec in secs.itertuples():
            s, e = sec.start, sec.end
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

        self.df_section = self.df_section.drop(rm_secs)
        self.df_tag = self.df_tag.drop(rm_tags)

        return newdoc

    def process(self, newdoc):
        paratextlist = []
        for i, sec in enumerate(self.df_section.itertuples()):
            st, se = sec.start, sec.end
            e = st
            part_tag = self.df_tag.loc[(self.df_tag.start >= st) & (self.df_tag.end <= se)]
            textlist = []
            for j, tag in enumerate(part_tag.itertuples()):
                s, e = tag.start, tag.end
                keys = [keytag(list(it.keys())[0], list(it.values())[0]) \
                        for it in eval(tag.taglist)]
                if newdoc[st: s]:
                    textlist += [token(newdoc[st: s], None, (st, s))]
                textlist += [token(newdoc[s: e], keys, (s, e))]
                st = e
            if newdoc[e: se]:
                textlist += [token(newdoc[e: sec.end], None, (e, sec.end))]
                e = se
            paratextlist.append(textlist)
        return paratextlist


def set_tag(tag):
    if isinstance(tag, list):
        reftag = ['xref', 'label']
        styletag = ['sub', 'sup', 'over', 'under', 'open', 'close']
        styletag2 = ['numerator', 'denominator', 'th', 'tr', 'td']
        fonttag = ['italic', 'bold', 'bold-italic', 'mi', 'fraktur',
                   'double-struck', 'script', 'sans-serif', 'bold-script',
                   'monospace', 'sc']  # , 'mo', 'mn'

        tag0 = []
        tag1 = []
        tag2 = []
        tag3 = []
        for t in tag:
            ttag = t.tag[:]
            if t.tag == 'mi':
                if t.attrs:
                    ttag = t.attrs.get('mathvariant')
                else:
                    ttag = 'italic'
                if ttag not in fonttag + ['normal']:
                    print(ttag)
            # pick out tags for WebAnno
            tag0 += [ref for ref in reftag if ref == ttag]
            tag1 += [style for style in styletag if style == ttag]
            tag2 += [style for style in styletag2 if style == ttag]
            tag3 += [font for font in fonttag if font == ttag]

        if not tag0:
            tag0 = '*'
        if not tag1:
            tag1 = '*'
        if not tag2:
            tag2 = '*'
        if not tag3:
            tag3 = '*'

        if tag0 == '*' and tag1 == '*' and tag2 == '*' and tag3 == '*':
            newtag = '_\t_\t_\t_'
        else:
            newtag = "|".join([t + '[NUM]' for t in tag0]) + \
                     '\t' + "|".join([t + '[NUM]' for t in tag1]) + \
                     '\t' + "|".join([t + '[NUM]' for t in tag2]) + \
                     '\t' + "|".join([t + '[NUM]' for t in tag3])
    else:
        newtag = '_\t_\t_\t_'
    return newtag


class OutFile:

    def __init__(self, paragraph_list, **kwargs):
        self.paragraph_list = paragraph_list
        self.outfile = kwargs['webannotsv']
        print('saved: ', self.outfile)

    def outputtsv(self):

        fw = self.outfile.open('w', encoding='utf-8')
        tsv_text = '#FORMAT=WebAnno TSV 3.2\n'
        tsv_text += '#T_SP=webanno.custom.Xml|label_tag|style_tag|style_tag2|font_tag\n\n\n'

        ntag = 0
        for i, elemlist in enumerate(self.paragraph_list):
            paratext = ''.join([elem.string.replace('\n', ' ')
                                for elem in elemlist]).rstrip(' ') + '\n'
            tsv_text += f'#Text={paratext}'
            k = 0
            prevtag = ''
            for j, elem in enumerate(elemlist):
                string, tag, offset = elem
                if tag is None or ('SP' not in tag and 'LF' not in tag):
                    newtag = set_tag(tag)
                    #                     if '_' not in newtag:
                    #                         print(i+1, j+1, elem.string, newtag)
                    if '_' not in newtag and prevtag != newtag:
                        ntag += 1
                    prevtag = newtag[:]
                    newtag = newtag.replace('NUM', str(ntag))
                    tsv_text += ('{}-{}\t{}-{}\t{}\t{}\t\n'.format(i + 1, k + 1,
                                                                   *offset,
                                                                   string,
                                                                   newtag))
                    k += 1
            tsv_text += '\n'
        print(tsv_text.rstrip('\n\n'), file=fw)


# split
def add_tag(tag, addtag):  # add tag
    newtag = tag
    if addtag is not None:
        if tag is None:
            newtag = [addtag]
        elif addtag not in tag and 'LF' not in tag:
            newtag = tag + [addtag]
    return newtag


def split2list(elem, RE_CHARA, addtag):
    text, tag, offset = elem
    textlist = []
    _text = []
    if RE_CHARA == prefix:
        index = [i for i, t in enumerate(text) if re.match(RE_CHARA, t) and i == 0]
    elif RE_CHARA == linefield or RE_CHARA == surfix or RE_CHARA == punct:
        index = [i for i, t in enumerate(text) if re.match(RE_CHARA, t) and i == len(text) - 1]
    elif RE_CHARA == infix:
        index = [i for i, t in enumerate(text) if re.match(RE_CHARA, t) and 0 < i < len(text) - 1]
    else:
        index = [i for i, t in enumerate(text) if re.match(RE_CHARA, t)]

    s = offset[0]
    for i in range(len(text)):
        if i in index:
            newtag = add_tag(tag, addtag)
            e = s + 1
            textlist += [token(text[i], newtag, (s, e))]
            s = e
        else:
            _text += [text[i]]
            if i + 1 in index or i == len(text) - 1:
                e = s + len(_text)
                textlist += [token(''.join(_text), tag, (s, e))]
                _text = []
                s = e

    assert e == offset[1], 'Offset is not correct!'
    return textlist


def splitby(textlist, comms):
    for command, attr in comms.items():
        newlist = []
        for n, dic in enumerate(textlist):
            newlist += split2list(dic, command, attr)
        textlist = newlist[:]
    #         print(command, attr, textlist[0])
    return textlist


# main
version = '20190524'
filedir = Path('../xml2text/textfiles/')
filelists = []
for fdir in filedir.iterdir():
    files = {
        'textfile': list(fdir.glob(f'*{version}.txt'))[0],
        'sectionfile': list(fdir.glob(f'*section_offset_{version}.csv'))[0],
        'tagfile': list(fdir.glob(f'*xmltag_offset_{version}.csv'))[0],
        'webannotsv': Path(fdir.name + f'_webanno_{version}.tsv')
    }
    filelists.append(files)

# tokenize conditions
linefield = re.compile(r'\n')
space = re.compile(r'\s')
punct = re.compile(r'[\,\.\:\;]')
blacs = '\\u0028\\u005B\\u003C\\u2039\\u27E8\\u3008'  # ( [  #〈  003C(<) 2039(‹) 27E8(⟨) 3008(〈)
blace = '\\u005D\\u0029\\u003E\\u203A\\u27E9\\u3009'  # ) ]  # 〉 003E(>) 203A(›) 27E9(⟩) 3009(〉)
blac = re.compile(fr'[{blacs}{blace}]')
infix = re.compile(r'[\u002F\u002D\u2215\u2192]')  # -/∕ →
prefix = re.compile(r'[\u002B\u002D\u003C-\u003E\u00B1\u2190-\u21FF\u2200-\u22FF]')
surfix = re.compile(
    r'[\u0025\u00B0\u002B\u002D\u003C-\u003E\u00B1\u2190-\u21FF\u2200-\u22FF]')  # %,°+-=<>±, Arrows, Relations

commands = {
    linefield: 'LF',
    space: 'SP',
    punct: None,
    blac: None,
    infix: None,
    prefix: None,
    surfix: None
}

# main loop
for i, filelist in enumerate(filelists[0:1]):

    print(i, filelist.get('textfile'))
    doc = ReadFile(**filelist)

    section = re.compile(r'TABLE(.+?)-body', re.I)  # remove sections (Table body)
    new_doc = doc.rmsections(section)
    para_text_list = doc.process(new_doc)

    new_para_elem_list = []
    for i, text_list in enumerate(para_text_list[:]):
        #     tok = TokenList(text_list)
        newlist = splitby(text_list, commands)
        new_para_elem_list.append(newlist)

    # output
    out = OutFile(new_para_elem_list, **filelist)
    out.outputtsv()
