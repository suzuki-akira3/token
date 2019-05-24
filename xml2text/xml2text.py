from pathlib import Path
from bs4 import BeautifulSoup
from collections import namedtuple

from modules import articleinfo, xmlparse, dicextract, process_math

# xdir = Path('/mnt/data/articles/aip/data/fy2018/')  # from age.nims.go.jp
xdir = Path('../articles/aip/data/fy2018/')  # For gitlab
assert xdir.exists(), 'Input directory is not correct!'
xmlfiles = [x for x in xdir.glob('**/*.xml')]
assert len(xmlfiles), 'No input files!'

# main loop
contents = []  # For articles info.
tagtext = namedtuple('elem', 'string tag')  # type(elem): string, type(tags): list

for i, file in enumerate(xmlfiles[0:1]):  # [2053:2054] for gitlab
    f = open(file, mode='r', encoding='utf-8')
    doc = f.read()
    # filename = str(file.relative_to('/mnt/data/'))
    filename = file.name
    print(i, filename)

    doc = xmlparse.pre_doc(doc)  # Pre-treatments for Beautifulsoup
    #     print(doc)
    soup = BeautifulSoup(doc, 'xml')
    soup = xmlparse.soup_treat(soup)  # Refine soup

    ###
    # extract metadata (article info.) of each article
    content = articleinfo.info_list(soup, filename)
    contents.append(content)

    dic_contents = {}  # texts and tags

    # Title
    title_text = soup.front.find('article-title')
    dic_contents['title'] = {}
    dic_contents['title']['paragraph-0'] = xmlparse.texts_tags(title_text)

    # Abstract
    dic_contents['abstract'] = {}
    if soup.abstract:
        abst = soup.abstract
        dic_contents['abstract'] = xmlparse.para_texts_tags(abst)

    # tables and figures
    dic_contents['tables'] = {}
    if soup.find('table-wrap'):
        for table in soup('table-wrap'):
            dic_contents['tables'].update(xmlparse.cap_texts(table))
            dic_contents['tables'].update(xmlparse.table_texts2(table))
            table.extract()

    dic_contents['figs'] = {}
    if soup.find('fig'):
        for fig in soup('fig'):
            dic_contents['figs'].update(xmlparse.cap_texts(fig))
            fig.extract()

    # Body
    dic_contents['sections'] = {}
    if soup.body:
        if soup.body.sec:
            for sec in soup.body('sec'):
                # set label+title
                ltitle = ''
                if sec.label:
                    ltitle = sec.label.get_text()
                if sec.title and sec.title.string and sec.title.string != 'NOMENCLATURE':
                    ltitle += sec.title.get_text()
                    dic_contents['sections'][ltitle] = xmlparse.para_texts_tags(sec)

        if soup.body('p', recursive=False):
            sec = soup.body('p', recursive=False)
            for ipara, paragraph in enumerate(sec):
                para = 'nosec-' + str(ipara)
                dic_contents['sections'][para] = xmlparse.texts_tags(paragraph)

        if soup.body.sec:
            if soup.body.sec.find('supplementary-material'):
                sec = soup.body.sec.find('supplementary-material')('p')
                for ipara, paragraph in enumerate(sec):
                    para = 'supplementary-' + str(ipara)
                    dic_contents['sections'][para] = xmlparse.texts_tags(paragraph)

            if soup.body.sec.glossary:
                if soup.body.sec.glossary.title:
                    ltitle = soup.body.sec.glossary.title.get_text()
                    dic_contents['glossary'] = {}
                    dic_contents['glossary'][ltitle] = {}
                    for it in soup.body.sec.glossary('def-item'):
                        if it.term:
                            key = it.term.get_text()
                            dic_contents['glossary'][ltitle][key] = xmlparse.texts_tags(it.find('def').p)

    dic_contents['appendix'] = {}
    if soup.find('app'):
        for app in soup('app'):
            # set label+title
            ltitle = ''
            if app.label:
                ltitle = app.label.get_text()
            if app.title:
                ltitle += app.title.get_text()
            dic_contents['appendix'][ltitle] = xmlparse.para_texts_tags(app)

    # save files
    doi = contents[i]['doi'].replace('/', '_')
    fdir = Path('./textfiles')  / doi
    dicextract.save_files(fdir, doi, dic_contents)