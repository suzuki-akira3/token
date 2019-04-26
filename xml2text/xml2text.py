from pathlib import Path
from bs4 import BeautifulSoup, NavigableString
from et_xmlfile import xmlfile

from modules import articleinfo, xmlparse, dicextract


xdir = Path('../articles/aip/data/fy2018/') # For gitlab
assert xdir.exists(), 'Input directory is not correct!'
xmlfiles = [x for x in xdir.glob('**/*.xml')] # fy2018 '**/vor_*.xml'
assert len(xmlfiles), 'No input files!'

### main loop
contents = [] # For articles info.
for i, file in enumerate(xmlfiles[0:1]): # [2053:2054] for age.nims.go.jp
    with file.open(mode='r', encoding='utf-8') as f:
        doc = f.read()
    # filename = str(file.relative_to('/mnt/data/'))
    print(i, file)
    
    doc = xmlparse.pre_doc(doc) # Pre-treatments for Beautifulsoup
    soup = BeautifulSoup(doc, 'xml')
    soup = xmlparse.soup_treat(soup) # Refine soup
#     if soup('mmultiscripts'): Reqiure implemanted!!!
#         for mm in soup('mmultiscripts'):
#             mm.replace_with(reorder_mmultiscpript(mm))

    # extract metadata (article info.) of each article
    content = articleinfo.info_list(soup, file)
    contents.append(content)

    dic_contents = {} # texts and tags
 
    ### Title
    title_text = soup.front.find('article-title')
    dic_contents['title'] = {}
    dic_contents['title']['paragraph-0'] = xmlparse.texts_tags(title_text)   

#     ### Abstract
    dic_contents['abstract'] = {}
    if soup.abstract:
        abst = soup.abstract
        dic_contents['abstract'] = xmlparse.para_texts_tags(abst)

        
    ### tables and figures
    dic_contents['tables'] = {}
    if soup.find('table-wrap'):
        for table in soup('table-wrap'):
            dic_contents['tables'].update(xmlparse.cap_texts(table)) # table captions
            dic_contents['tables'].update(xmlparse.table_texts(table)) # table bodies
            table.extract()  # extract table tags from soup

    dic_contents['figs'] = {}
    if soup.find('fig'):
        for fig in soup('fig'):
            dic_contents['figs'].update(xmlparse.cap_texts(fig)) # figure captions
            fig.extract() # extract fig tags from soup
            
    
    ### Body
    dic_contents['sections'] = {}
    if soup.sec:
        for sec in soup('sec'):
            # set label+title
            ltitle = ''
            if sec.label:
                ltitle = sec.label.get_text()
            if sec.title:
                ltitle += sec.title.get_text()
            
            dic_contents['sections'][ltitle] = xmlparse.para_texts_tags(sec)
    else:
        if soup.body('p'): # in case of no sec tags
            sec = soup.body
            dic_contents['sections']['nosec'] = xmlparse.para_texts_tags(sec)

    ### Appendix
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

    ### Equations
    # under development
            
    ### save files
    doi = contents[i]['doi'].replace('/', '_')
    dicextract.save_files(doi, dic_contents)     