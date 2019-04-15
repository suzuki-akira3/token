from pathlib2 import Path
import re
from collections import OrderedDict
import json

class dotdict(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__dict__ = self

file = Path('./10.1063_1.1774263_jats.txt')
with file.open(encoding='utf-8') as f:
    doc = f.read()

splitLineSpace = re.finditer(r'(?P<TX>[^\n]+)(?P<LF>\n)', doc)
textList = [chunk.groupdict() for chunk in splitLineSpace]
# print(textList)

for i, dicText in enumerate(textList):
    splitspaces = re.finditer(r'(?P<TK>[^\s]+?)(?P<SP>\s)',dicText['TX'])
    token_list = [ss.groupdict() for ss in splitspaces]
    dicText['TX'] = token_list
print(textList)

#
# for token_ in token_list:
#     print(token_)
#     puncts = re.match(r'(.+?)([\.\,\;\:]$)', token_[0])
#     if puncts:
#         print('\t\t', list(puncts.groups()) + [token_[1]])
#     else:
#         print('\t', token_)




