import re
from pathlib import Path
from bs4 import BeautifulSoup, NavigableString
import pandas as pd
from itertools import chain
from collections import Counter
import datetime


def offset(off_list, txt):
    off_list[0] = off_list[1]
    off_list[1] = off_list[0] + len(str(txt))
    return off_list


def xmloffset(val, off, lst):
    for v in val:
        offset(off, v[0])
        if len(v)>1:
            lst.append((v[0], v[1:], *tuple(off))) 
    offset(off, '\n')
    return lst


def getoffset(title, cts, off_sec, off): # add '\n' to texts
    txt = []; offs = []; lst = []  
    for ky, val in cts.items():
        if not re.search('paragraph-', ky): # Select sec title
            if not re.match(r'table(.+?)-body|nosec', ky, re.I): # Exclude TABLE-body titile
                txt.append(ky+'\n') # add '\n' to texts
                # section offsets
                offset(off_sec, ky+'\n')
                offs.append((ky, *tuple(off_sec)))
                # xml offsets
                lst = xmloffset(ky, off, lst) # tags in title
            for ky2, val2 in val.items(): # sec contents
                if len(val2[0])>0:
                    tx = ''.join([v[0] for v in val2]) + '\n'  # add '\n' to texts
                    txt.append(tx)
                    # section offsets
                    offset(off_sec, tx) 
                    ti = ky + ky2[-2:] # Introduction + -0
                    offs.append((ti, *tuple(off_sec)))
                    # xml offsets
                    lst = xmloffset(val2, off, lst)
        else: # Select Title, Abstract
            tx = ''.join([v[0] for v in val]) + '\n'  # add '\n' to texts
            txt.append(tx)
            # section offsets
            offset(off_sec, tx)
            offs.append((title, *tuple(off_sec)))
            # xml offsets
            lst = xmloffset(val, off, lst)          
    return [txt, offs, lst]


def save_files(doi, dic_contents):

    off = [0, 0]
    off_sec = [0, 0]
    alltexts_list = []
    xmloffsets_list = []
    secoffsets_list = []
    
    datetime_format = datetime.date.today()
    version = datetime_format.strftime("%Y%m%d")

    titles = ['title', 'abstract', 'sections', 'appendix', 'tables', 'figs']

    for title in titles:
        if title in dic_contents:
            cts = dic_contents[title]
            [text, secoff, xmloff] = getoffset(title, cts, off_sec, off)
            alltexts_list.append(text)
            secoffsets_list.append(secoff)
            xmloffsets_list.append(xmloff)

    alltexts = (''.join(chain.from_iterable(alltexts_list)))

    textfile = f'{doi}_fulltext_{version}.txt'
    secoffset = f'{doi}_section_offset_{version}.csv'
    xmltagoffset = f'{doi}_xmltag_offset_{version}.csv'
    
    with open(textfile, mode='w', encoding='utf-8') as fw:
        print(alltexts, file=fw)

    df_sec = pd.DataFrame(list(chain.from_iterable(secoffsets_list)), columns=['sec_title', 'start', 'end'])     
    df_tag = pd.DataFrame(list(chain.from_iterable(xmloffsets_list)), columns=['word', 'taglist', 'start', 'end'])
    
    # export json files
    secoffset_json = f'{doi}_section_offset_{version}.json'
    xmltagoffset_json = f'{doi}_xmltag_offset_{version}.json'
    
    df_sec.to_json(secoffset_json)
    df_tag.to_json(xmltagoffset_json)
    
    # export csv files
    df_sec = df_sec.set_index('sec_title')
    df_sec.to_csv(secoffset)
    df_tag = df_tag.set_index('word')
    df_tag.to_csv(xmltagoffset)

