class TagText:
    def __init__(self):
        self.tag = tag
        self.text = text

    def makedic(self, tag, text):
        return {self.tag : self.text}


tag = 'TX'
text = 'text'
dic = {tag : text}
a = TagText()
a.makedic(tag, text)


class Manage:
    def __init__(self):
        self.textlist = []
        self split = SplitBy()



    para_textlist = []
    for dic in text_list:
        if 'TX' in dic.keys():
            para_textlist += splitparagraph(dic)
        else:
            para_textlist += [dic]

    para_tokenlist = []
    for dic_para in para_textlist:
        if 'TX' in dic_para.keys():
            para_tokenlist += splitbyspace(dic_para)
        else:
            para_tokenlist += [dic_para]

    punk_tokenlist = []
    for dic_pn in para_tokenlist:
        if 'TK' in dic_pn.keys():
            punk_tokenlist += splitbypunct(dic_pn)
        else:
            punk_tokenlist += [dic_pn]

    blac_tokenlist = []
    for dic_bl in punk_tokenlist:
        if 'TK' in dic_bl.keys():
            blac_tokenlist += splitbyblacket2(dic_bl)
        else:
            blac_tokenlist += [dic_bl]

    infix_tokenlist = []
    for dic_if in blac_tokenlist:
        if 'TK' in dic_if.keys():
            infix_tokenlist += splitbyinfix(dic_if)
        else:
            infix_tokenlist += [dic_if]

prefix_tokenlist = []
for dic_pr in infix_tokenlist:
    if 'TK' in dic_pr.keys():
        prefix_tokenlist += splitbyprefix2(dic_pr)
    else:
        prefix_tokenlist += [dic_pr]

surfix_tokenlist = []
for dic_sr in prefix_tokenlist:
    if 'TK' in dic_sr.keys():
        surfix_tokenlist += splitbysurfix2(dic_sr)
    else:
        surfix_tokenlist += [dic_sr]






class SplitBy:
    def __init__(self):
        self.dic = {}

    def space(text):
        if re.search(r'\s', text):
            splitspaces = re.finditer(r'(?P<TK>[^\s]+)(?P<SP>\s)?|(?P<SP2>\s)?', text)
            for ss in splitspaces:
                return [{k[0:2]: v} for k, v in ss.groupdict(default='').items() if v]

    def punct(text):
        splitpunct = re.match(r'(?P<TK>.+?)(?P<PN>[,.:;]$)', text)
        if splitpunct:
            #         print(splitpunct.groupdict(default=''))
            return [{k: v} for k, v in splitpunct.groupdict(default='').items() if v]

# main
dirname = Path('../xmltext')
file = Path(dirname / '10.1063_1.5004600_fulltext_20190405.txt')
with file.open(encoding='utf-8') as f:
    doc = f.read()
df_sections = pd.read_csv(dirname / '10.1063_1.5004600_section_offset_20190405.csv')
df_tags = pd.read_csv(dirname / '10.1063_1.5004600_xmltag_offset_20190405.csv')

section = r'TABLE(.+?)-body'  # remove sections
new_doc = rmsections(section)

text_list = splitxmltags(new_doc)

textlist = []
text = list(dic.values())[0]