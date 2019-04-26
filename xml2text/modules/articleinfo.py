import json
import collections as cl
from bs4 import BeautifulSoup, NavigableString

def exstring(s):
    return [s.get_text() if s else ''][0]


def info_list(soup, filename):
    ### front
    ### DOI
    doi = exstring(soup.front.find('article-id', {'pub-id-type': 'doi'}))
    
    ### Journal
    journal = exstring(soup.front.find('journal-title'))
    abbrev_journal = exstring(soup.front.find('abbrev-journal-title'))
    
    ### vol, issue, elocation, and pub year 
    vol = exstring(soup.front.volume)
    issue = exstring(soup.front.issue)
    elocation = exstring(soup.front.find('elocation-id'))
    year = exstring(soup.front.find('pub-date').year)
    month = exstring(soup.front.find('pub-date').month)
    day = exstring(soup.front.find('pub-date').day)

    ### Authors
    contribs = soup.front('contrib', {'contrib-type': 'author'})
    authors = [] # given-names, surname
    for au in contribs:
        if au.find('given-names'):
            author = exstring(au.find('given-names')) + ' ' + exstring(au.surname)
        else:
            author =  exstring(au.surname)
        authors.append(author)
            
    ### Affiliation
    affiliation = ''
    if soup.front.aff:
        if soup.front.aff.label:
            aff = soup.front.aff.label.extract()
        affiliation = exstring(soup.front.aff)
    
    ### Title
    title_text = soup.front.find('article-title').get_text() # タイトル文をテキストとして抽出 

    content = dict({'doi':doi, 
               'filename': filename, 
               'journal' : journal,
               'abb_journal' : abbrev_journal,
               'vol' : vol, 
               'issue' : issue, 
               'location' : elocation, 
               'published' : '/'.join([year, month, day]), 
               'authors' : ', '.join(authors), 
               'affiliation': affiliation, 
               'title' : title_text})
    return(content)