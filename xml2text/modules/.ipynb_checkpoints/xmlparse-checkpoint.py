### def files
###　実体参照（&amp;）の文字変換追加　要entitles.json読み込み

import re
from pathlib import Path
from bs4 import BeautifulSoup
from bs4 import NavigableString
import numpy as np
import pandas as pd
import json
import collections as cl    
import html

def exstring(s):
    return [s.get_text() if s else ''][0]

def add_pstr(tag, s): # 前に文字列sを追加
    for w in tag:
        w.insert(0, s)

def add_str(tag, s): # 後に文字列sを追加
    for w in tag:
        w.append(s)      
        
def pre_doc(t): # docの調整用
    t =  re.sub(r'\s\s+',' ',t) # 複数スペースを1個に
    t =  re.sub(r'\n\n+','\n',t) # 複数改行を1個に
    t = re.sub(r'>\s+<', '><', t) # タグ間のスペースを削除
    t = re.sub(r'>\n', '>', t) # タグ後の改行を削除             
    return(t)

def soup_treat(s): # soupの調整用
    add_str(s('mspace'), ' ') # スペースをmspaceタグで囲う
    add_pstr(s('xref', {'ref-type':'bibr'}), ' [') # 文献番号を[]で囲う [の前にスペース[
    add_str(s('xref', {'ref-type':'bibr'}), ']') # 文献番号を[]で囲う
    disp = s('disp-formula') # 数式：disp-formulaを削除して改行を挿入
    for w in disp: 
        w.string = '\n'
    #
    add_str(s('label'), ' ') # labelの後にスペース
    add_pstr(s('list-item'), '\n') # list-itemの前に改行

    ### mmultiscript
    mmultiscripts = s('mmultiscripts')
    for mm in mmultiscripts:
        if len(mm.contents) > 2:
            mm.string = get_mmultiscripts(mm.contents)
#         print(mm.string)
        
    ### modify sup & sub-script    
    informula = s('inline-formula') or []
    for formula in informula:
        math_msup(formula)  # 順番 msup -> msub ?  
        math_msub(formula)  
    return(s)


def subsup(s):
    tags = list(s('sub'))
    for tag in tags[::-1]:
        if tag.parent.name != 'xref':
            c = exstring(tag)
            tag.string = '_{{{}}}'.format(c)
    tags = list(s('sup'))
    for tag in tags[::-1]:
        if tag.parent.name != 'xref':        
            c = exstring(tag)
            tag.string = '^{{{}}}'.format(c)
    return s
            

def text_clean(s): # 出力テキストの整形用、文献番号の調整
    s = s.rstrip()
    s = re.sub(r'\n\n+', '\n', s)
    s = re.sub(r'^\n', '', s)
    s = s.replace(' et al.', ' et_al') # et al. のピリオドが邪魔なため
    ###
    refp = re.finditer(r'([Rr]efs?)\. ', s) # Ref. のピリオドが邪魔なため
    for ref in refp:
#         print(ref.group(0))
        s = s.replace(ref.group(0), ref.group(0)[:-2])
    refs = re.finditer(r'[\.\,\;\:] \[\d\d?\]|[\.\,\;\:] \[\d+–\d+\]|[\.\,\;\:] \[\d+[\,–][\d\,–]*\]', s) # 文献番号を[.,;:]の前に　sentence. [11] ⇒ sentence [11].
    for ref in refs:
        p1 = ref.group(0)
        p2 = p1[1:] + p1[0:1]
        s = s.replace(p1, p2)
    return s


def body_texts(body): # beautifulsoup body/sec処理
    dic = cl.OrderedDict({})
    dic2 = cl.OrderedDict({})
    for i, child in enumerate(body):
        ### NOMENCLATURE
        if child.glossary:
            deftitle = exstring(child.glossary.title)
            defitems = child.glossary('def-item')
            dtexts = []
            for defitem in defitems:
                defterms = defitem('term')
                defps = defitem('def')
                for (defterm, defp) in zip(defterms, defps):
                    dtexts.append('{}\t{}'.format(defterm.get_text(), defp.get_text()))
            dic[deftitle] = dtexts
            child.glossary.extract()
        ### BODY
        sl = child.find('label', recursive=False)
        sec_label = exstring(sl)
        if child.title:
            sec_title = sec_label + child.title.get_text()
        else:
            sec_title = 'Notitle-' + str(i) # section titleが無い場合の対策
        texts = []
        if child('p'):
            for p in child('p', recursive=False):
                text = p.get_text()
                text = text_clean(text)
                texts.append(text)
        dic2[sec_title] = texts
        dic.update(dic2)
    return dic


def label_texts(items): # beautifulsoup caption処理 for fy2018
    dic = cl.OrderedDict({})
    for item in items:
        if item.label:
            label = item.label.get_text()
        else:
            label = 'None' # labelが無いことは想定していない
        texts = []
        if item.caption:
            if item.caption('p'):
                for p in item.caption('p'):
                    text = item.caption.p.get_text()
                    text = text_clean(text)
                    texts.append(text)
        dic[label] = texts
    return dic


def table_texts(items): # beautifulsoup table本体処理
    dic = cl.OrderedDict({})
    for item in items:
        if item.label:
            label = item.label.get_text() + '-body' # labelがキャプションと重複しないようにするため
        else:
            label = 'None' # labelが無いことは想定していない
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
                if chfoot.name == 'label': labelfoot = exstring(chfoot)
                if chfoot.name == 'p': texts.append(labelfoot + exstring(chfoot))
        dic[label] = texts
    return dic


def appendix_texts(body): # beautifulsoup Appendix処理
    dic = cl.OrderedDict({})
    for i, child in enumerate(body):
        sl = child.find('label', recursive=False)
        sec_label = exstring(sl)
        if child.title:
            sec_title = sec_label + child.title.get_text()
        else:
            sec_title = 'Notitle-' + str(i) # section titleが無い場合の対策
        texts = []
        if child('sec'): # secがある場合とない場合あり
            for s in child('sec'):
                if s('p'):
                    for p in s('p', recursive=False):
                        text = p.get_text()
                        text = text_clean(text)
                        texts.append(text)
        elif child('p'):
            for p in child('p', recursive=False):
                text = p.get_text()
                text = text_clean(text)
                texts.append(text)            
        dic[sec_title] = texts
    return dic


def output_texts(f, content, all_texts): # Output text files
    f.parents[0].mkdir(parents=True, exist_ok=True)
    with f.open(mode='w', encoding='utf-8') as ft:
#         print('# {} {} {} {} {} {}'.format(content['doi'], content['abb_journal'], content['vol'], content['issue'], \
#                                                content['location'], content['published']), file=ft)
        print('\n'.join(all_texts), file=ft)
