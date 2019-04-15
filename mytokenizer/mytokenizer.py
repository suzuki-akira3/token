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

splitLineSpace = re.finditer(r'([^\n]+)(\n)', doc)
textList = [OrderedDict({'TX': chunk.group(1), 'LF':chunk.group(2)}) for chunk in splitLineSpace]

for i, dicText in enumerate(textList):
    splitspaces = re.finditer(r'([^\s]+?)(\s)',dicText['TX'])
    token_list = []
    for ss in splitspaces:
        dic = OrderedDict( {'TK': ss.group(1), 'SP': ss.group(2)})
        token_list.append(dic)
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




