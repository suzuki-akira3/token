from pathlib2 import Path
import re
import json

file = Path('./10.1063_1.1774263_jats.txt')
with file.open(encoding='utf-8') as f:
    doc = f.read()

splitspaces = re.finditer(r'([^\s]+?)(\s)', doc)
token_list = []
for ss in splitspaces:
    token_list.append([w for w in ss.groups()])

for token_ in token_list:
    token = ''.join(token_)
    puncts = re.match(r'([/+?])([\.\,\;\:])', token)
    if puncts:
        print(puncts.groups())