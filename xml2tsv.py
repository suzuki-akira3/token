# transform tei to tsv for WebAnno
import os
import re
from pathlib import Path
from itertools import chain
from bs4 import BeautifulSoup, NavigableString, Tag


def my_tokenizer(string):

    tokens_match = re.finditer(r'(?P<g0> ?)(?P<term>.+?)(?P<g2> )|(?P<term1>.+)', string)  # split by a space
    token_list = []
    for token in tokens_match:
        subtoken_list = []
        sub_tokens_match = token.groups(default='')
        for subtoken in [s for s in sub_tokens_match if s]:
            #             print(subtoken)
            if subtoken == ' ':
                if len(subtoken_list) > 0:
                    subtoken_list[-1] += ' '
                else:
                    subtoken_list += [subtoken]
            else:
                peri = re.match(r'(?P<term>[^\.]+)(?P<peri>[\.\,\:\;]$)', subtoken)
                if peri:
                    term = peri.group(1)
                    suf = peri.group(2)
                else:
                    term = subtoken
                    suf = ''

                mblac = re.match(r'\[\w+\](\[\w+\])+', term)
                blac = re.match(
                    r'(?P<blacs>[“\(\[])(?P<term>[^\(\)\[\]]+)(?P<blace>[”\)\]])|(?:(^[“\(\[])([^\(\)\[\]]+)?)|(?:([^\(\)\[\]]+)?([”\)\]])$)',
                    term)
                if mblac:
                    subtoken_list += [mblac.group()]
                elif blac:
                    subs = [w for w in blac.groups(default='') if w]
                    subtoken_list += [s for s in subs]
                else:
                    subtoken_list += [term]

                if suf:
                    subtoken_list += [suf]
                #                 print(subtoken_list)
        token_list += [w for w in subtoken_list]

    return token_list


def processFile(input, output):
    entity_dic = {
        'shape': 'shape',
        'supercon': 'supercon',
        'tc': 'tc',
        'propertyOther': 'propertyOther',
        'substitution': 'substitution',
        'propertyValue': 'propertyValue',
        '_': '_'
    }

    with open(input, 'r', encoding='utf-8') as fp:
        doc = fp.read()

    mod_tags = re.finditer(r'(</\w+>) ', doc)
    for mod in mod_tags:
        doc = doc.replace(mod.group(), ' ' + mod.group(1))
    #     print(doc)
    soup = BeautifulSoup(doc, 'xml')

    fw = open(output, 'w', encoding='utf-8')
    print('#FORMAT=WebAnno TSV 3.2', file=fw)
    print('#T_SP=webanno.custom.Supercon|supercon_tag\n\n', file=fw)

    root = None
    for child in soup.tei.children:
        if child.name == 'text':
            root = child

    off_token = 0
    tsvText = ''
    labels = []
    dic_token = {}
    ient = 1
    for i, pTag in enumerate(root('p')):
        j = 0
        paragraphText = ''
        for item in pTag.contents:
            if type(item) == NavigableString:
                paragraphText += str(item)

                token_list = my_tokenizer(item.string)

                entity = '_'
                for token in token_list:
                    s = off_token
                    off_token += len(token.rstrip(' '))
                    e = off_token
                    dic_token[(i + 1, j + 1)] = (s, e, token.rstrip(' '), entity_dic.get(entity))
                    #                     print((i+1, j+1), s, e, [token], len(token.rstrip(' ')), off_token)
                    if token[-1] == ' ':
                        off_token += 1  #
                    j += 1
            elif type(item) is Tag:
                paragraphText += item.text

                token_list = my_tokenizer(item.string)
                entity = item.name
                for token in token_list:
                    s = off_token
                    off_token += len(token.rstrip(' '))
                    e = off_token
                    dic_token[(i + 1, j + 1)] = (
                    s, e, token.rstrip(' '), entity_dic.get(entity) + f'[{ient}]')  # entity_dic.get(entity)+f'[{ient}]'
                    #                     print((i+1, j+1), s, e, [token], len(token.rstrip(' ')), off_token)
                    if token[-1] == ' ':
                        off_token += 1  #
                    j += 1
                ient += 1  # entity No.

        off_token += 1  # return

        tsvText += (f'#Text={paragraphText}\n')
        print(f'#Text={paragraphText}', file=fw)
        for (k, v) in dic_token.items():
            if k[0] == i + 1:
                print('{}-{}\t{}-{}\t{}\t{}\t'.format(*k, *v), file=fw)
        if i != len(root('p')) - 1:
            print('', file=fw)


input = './xmlfiles/'
output = './Webanno_tsv/'

if os.path.isdir(input):
    if not os.path.exists(output):
        print("output directory does not exists, creating it!")
        os.mkdir(output)

    pathlist = Path(input).glob('*.tei.xml')
    for path in pathlist:
        print(path)
        path_in_str = str(path)
        processFile(path_in_str, output + '/' + str(path.name) + ".tsv")