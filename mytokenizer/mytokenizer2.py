import re

RE_LF = re.compile(r'(?P<TX>[^\n]+)(?P<LF>\n)')
RE_PN = re.compile(r'(?P<TX>[^\.\,\:\;]+)(?P<PN>[\.\,\:\;])')
RE_SP = re.compile(r'(?P<TK>[^\s]+)(?P<SP>\s)')


class ReadFiles:
    def __init__(self, filename='u.txt'):
        with open(filename, 'r', encoding='utf-8') as f:
            self.text = f.read()
            self.paragraph = [m.groupdict(default='') for m in RE_LF.finditer(self.text)]
            self.textlist = []
            self.tokenlist = []

    def __len__(self):
        return len(self.paragraph)

    def __getitem__(self, index):
        return self.paragraph[index]

    def __repr__(self):
        return self.text

    def offset(self, offset):
        return self.text[slice(*offset)]

    def splitbypn(self):
        for paradic in self.paragraph:
            if 'TX' in paradic.keys():
                match = RE_PN.match(list(paradic.values())[0])
                if match:
                    self.textlist += [match.groupdict(default='')]
                else:
                    self.textlist += [{'TX': list(paradic.values())[0]}]
            else:
                self.textlist += [paradic]
        return self.textlist

    def splitbysp(self):
        for textdic in self.textlist:
            if 'TX' in textdic.keys():
                if RE_SP.search(list(textdic.values())[0]):
                    matches = RE_SP.finditer(list(textdic.values())[0])
                    for match in matches:
                        self.tokenlist += [match.groupdict(default='')]
                else:
                    self.tokenlist += [{'TK': list(textdic.values())[0]}]
            else:
                self.tokenlist += [textdic]
        return self.tokenlist


t = ReadFiles()
t.offset((0, 10))
t.splitbypn()
t.splitbysp()