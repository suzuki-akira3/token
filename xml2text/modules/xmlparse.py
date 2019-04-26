import re
from pathlib import Path
from bs4 import BeautifulSoup, NavigableString
import pandas as pd
from itertools import chain
from collections import Counter


def add_pstr(tag, s):  # 前に文字列sを追加
    for w in tag:
        w.insert(0, s)


def add_str(tag, s):  # 後に文字列sを追加
    for w in tag:
        w.append(s)


def pre_doc(t):  # remove extra spaces and line fields to avoid wrong extraction of texts
    t = re.sub(r'\s\s+', ' ', t)  # make multiple spaces to single
    t = re.sub(r'\n\n+', '\n', t)  # make multiple line fields to single
    t = re.sub(r'>\s+<', '><', t)  # remove space(s) between two sequential tags
    t = re.sub(r'>\n', '>', t)  # remove line field after tags
    return t


def soup_treat(s):  # soupの調整用
    add_str(s('mspace'), '\u2009')  # スペースをmspaceタグで囲う
    disp = s('disp-formula')  # 数式：disp-formulaを削除 後で処理を追加
    for w in disp:
        w.string = ''
    #
    add_str(s('label'), ' ')  # labelの後にスペース
    add_pstr(s('list-item'), '\n')  # list-itemの前に改行
    return s


def reorder_mmultiscpript(mm):
    ind = [i for i, _x in enumerate(mm) if '<mml:mprescripts/>' in str(_x)][0]
    mm.contents = mm.contents[ind + 1:] + mm.contents[:ind]
    return mm


# Extract texts and tags as list format [text..., [text, tags], ...]
def texts_tags(para):
    dic = {}
    tag_list = list(para.descendants)
    i = len(tag_list) - 1  # reverse numbering for sorting process
    j = i + 1  # dummy
    dic[i] = {}
    for pp in tag_list[::-1]:  # extract tags in reverse order
        if isinstance(pp, NavigableString):
            dic[i] = [pp.string]
            j = i  # j is index number of tags, and it is as same number as that of text
            i -= 1
        else:
            #             print(pp.name, pp.attrs, isinstance(pp.string, NavigableString))
            if isinstance(pp.string, NavigableString):
                if pp.attrs:
                    dic[j] += [{pp.name: pp.attrs}]
                else:
                    dic[j] += [pp.name]
            i -= 1
    return [v for k, v in sorted(dic.items())]  # dictionary for texts and tags in normal order


def para_texts_tags(tag):
    dic = {}
    paragraphs = ([p for p in tag('p', recursive=False)])
    for ipara, paragraph in enumerate(paragraphs):
        if paragraph.find('disp-formula'):
            for disp in paragraph('disp-formula'):
                disp = disp.replace_with('')  # add process for disp-formula later!
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


def table_texts(item):  # beautifulsoup process for table-body under development!
    dic = {}
    if item.label:
        label = item.label.get_text() + '-body'  # labelがキャプションと重複しないようにするため
    else:
        label = 'None'  # labelが無いことは想定していない
    texts = []
    for it in item('tr'):
        tcol = []
        for w in it('th'):
            tcol.append(w.get_text())
        for w in it('td'):
            tcol.append(w.get_text())
        texts.append('\t'.join(tcol))
        # table footer
    if item.find('table-wrap-foot'):
        labelfoot = ''
        for chfoot in item.find('table-wrap-foot').descendants:
            if chfoot.name == 'label': labelfoot = chfoot.get_text()
            if chfoot.name == 'p': texts.append(labelfoot + chfoot.get_text())  # tag offset まだ！
    dic[label] = {}
    dic[label]['paragraph-0'] = [['\n'.join(texts)]]
    return dic
