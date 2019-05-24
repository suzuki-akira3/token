import re
from pathlib import Path
from bs4 import BeautifulSoup, NavigableString
import pandas as pd
from itertools import chain
from collections import Counter

from collections import namedtuple

tagtext = namedtuple('elem', 'string tag')  # type(elem): string, type(tags): list

from modules import process_math


def add_pstr(tag, s):  # 前に文字列sを追加
    for w in tag:
        w.insert(0, s)


def add_str(tag, s):  # 後に文字列sを追加
    for w in tag:
        w.append(s)


def pre_doc(t):  # remove extra spaces and line fields to avoid wrong extraction of texts
    t = re.sub(r'>\s*\n\s*<', '><', t)  # remove line field and spaces between tags
    t = re.sub(r'\s\s+', ' ', t)  # make multiple spaces to single
    t = re.sub(r'\n\n+', '\n', t)  # make multiple line fields to single
    RE = re.compile(r'(?<!</disp-formula>)<disp-formula id="d\d+"><mml:math display="block" overflow="scroll">')
    matches = re.finditer(RE, t)
    for m in matches:
        t = t.replace(m.group(), m.group() + '\n')  # add \n before disp-formula
    return (t)


def soup_treat(s):  # soupの調整用
    #     add_str(s('mspace'), '\u2009') # スペースをmspaceタグで囲う
    disps = s('disp-formula')  # 数式：disp-formulaの前に改行を追加
    for disp in disps:
        disp.contents = [d for d in disp.contents if d.name]  # remove dusts
        if disp.math:
            #             add_pstr(disp('math'), '\n')
            add_pstr(disp('label'), ' ')
            add_str(disp('label'), '\n')
    #
    if s.sec and s.sec.label:
        add_str(s.sec('label'), ' ')  # section labelの後にスペース
    add_pstr(s('list-item'), '\n')  # list-itemの前に改行
    return s


def intags(item, newtag):
    if isinstance(item, NavigableString):
        return [tagtext(item, None)]
    else:
        tlist = []
        for it in item:
            if isinstance(it, NavigableString):
                if {item.name: item.attrs} not in newtag:
                    newtag += [{item.name: item.attrs}]
                tlist += [tagtext(it, newtag)]
            else:
                newtag2 = newtag[:]  # they should not be an identical id
                if {item.name: item.attrs} not in newtag:
                    newtag2 += [{item.name: item.attrs}]
                tlist += intags(it, newtag2)
        return tlist


# Extract texts and tag as a namedtuple; tagtext
def texts_tags(items):
    tuplist = []
    for item in items:
        if item.name == 'inline-formula' or item.name == 'disp-formula':  # for formula
            if item.math:
                tuplist += process_math.process_mathml(item.math)
                if item.label:
                    tuplist += [tagtext(''.join(item.label.contents[:]),
                                        [{item.label.name: 'disp-formula'}])]
            elif item.find('tex-math'):
                tuplist += process_math.process_texmath(item.find('tex-math'))
            else:
                if item.string:
                    tuplist += [tagtext(item.string, None)]
        #                 if not item.find('inline-graphic') :
        #                     tuplist += tagtext(item.get_text(), [{'math' : 'other'}])
        else:  # for xml tag and text
            tuplist += intags(item, newtag=[])

    return tuplist


def para_texts_tags(tag):
    dic = {}
    #     add_str(tag('p', recursive=False), '\n')  # add '\n' at the end of paragraph
    paragraphs = ([p for p in tag('p', recursive=False)])
    for ipara, paragraph in enumerate(paragraphs):
        #         if paragraph.find('disp-formula'):
        #             for disp in paragraph('disp-formula'):
        #                 disp = disp.replace_with('') # add process for disp-formula later!
        para = 'paragraph-' + str(ipara)
        dic[para] = texts_tags(paragraph)
    return dic


def cap_texts(item):  # beautifulsoup caption
    dic = {}
    if item.label:
        label = item.label.get_text()
    else:
        label = 'None'  # labelが無いことは想定していない
    if item.caption:
        dic[label] = para_texts_tags(item.caption)
    return dic


def table_texts2(item):  # beautifulsoup table本体処理
    dic = {}
    if item.label:
        label = item.label.get_text() + '-body'  # labelがキャプションと重複しないようにするため
    else:
        label = 'None'  # labelが無いことは想定していない
    texts = []
    for it in item('tr'):
        texts += texts_tags(it)
    #     texts += [tagtext('\n', None)]

    # table fotter
    if item.find('table-wrap-foot'):
        labelfoot = ''
        footer = item.find('table-wrap-foot')
        for chfoot in footer.contents:
            texts += texts_tags(chfoot)
        #         texts += [tagtext('\n', None)]

    dic[label] = {}
    dic[label]['paragraph-0'] = texts
    return dic
