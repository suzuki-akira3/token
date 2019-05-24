## process_mathml
# tagtext = namedtuple('elem', 'string tag')  # type(elem): string, type(tags): list

from bs4 import BeautifulSoup, NavigableString
from collections import namedtuple

tagtext = namedtuple('elem', 'string tag')  # type(elem): string, type(tags): list

def process_mathml(math):
    taglist = []
    if isinstance(math, NavigableString):
        taglist += [tagtext(math, {'string' : 'mathML'})]
    else:
        for j, m in enumerate(math):
            t = eval(m.name)(m)
            taglist += set_taglist(t, {'tag' : 'mathML'})
    return taglist

            
def process_texmath(math):
    return [tagtext(math.string, {'math' : 'tex-math'})]


def eval_content2(m):
    if isinstance(m, NavigableString):
        return eval(m.parent.name)(m.parent)
    else:
        return eval(m.name)(m)   

    
def set_taglist(m, addtag):  # add tag
    taglist = []
    for mm in m:
        newtag = mm.tag + [addtag]  #if addtag else mm.tag
        taglist += [tagtext(mm.string, newtag)]
    return taglist
        

# process for mathML

def mspace(m):
    return [tagtext('\u2009',  [{m.name : m.attrs}])]


def mrow(m):
    taglist = []
    for mm in m.contents:
        if mm.name:
            taglist += eval(mm.name)(mm)
    return taglist

        
def mo(m):
    return [tagtext(m.string,  [{m.name : m.attrs}])]


def mn(m):
    return [tagtext(m.string,  [{m.name : m.attrs}])]


def mi(m):
    return [tagtext(m.string,  [{m.name : m.attrs}])]


def mtext(m):
    return [tagtext(m.string,  [{m.name : m.attrs.get('mathvariant')}])]


def mstyle(m):
    taglist = []
    for t in m.contents:
        newtag = [{t.name : t.attrs}]
        taglist += [tagtext(t.string, newtag)]
    return taglist


def mover(m):
    movers = m.contents
    if len(movers) == 2:
        taglist = []
        for mo in movers[0]:
            t = eval_content2(mo)  # check if eval_contents2 works !
            taglist += set_taglist(t, {'base' : m.name})
        for mo in movers[1]:
            t = eval_content2(mo)  # check if eval_contents2 works !
            taglist += set_taglist(t, {'over' : m.name})
        return taglist
    else:
        return [tagtext(m.get_text(),  [{m.name : m.attrs}]) ]   

    
def munder(m):
    taglist = []
    for under in m:
        t = eval_content2(under)
        taglist += set_taglist(t, {'under' : m.name})
    return taglist


def munderover(m):
    uos = m.contents
    if len(uos) == 3:
        taglist = []
        for uo in uos[0]:
            t = eval_content2(uo)
            taglist += set_taglist(t, {'base' : m.name}) 
        for uo in uos[1]:
            t = eval_content2(uo)
            taglist += set_taglist(t, {'under' : m.name}) 
        for uo in uos[2]:
            t = eval_content2(uo)
            taglist += set_taglist(t, {'over' : m.name})    
        return taglist
    else:
        return [tagtext(m.get_text(),  [{m.name : m.attrs}])]


def msub(m):
    subs = m.contents
    if len(subs) == 2:
        taglist = []
        for sub in subs[0]:
            t = eval_content2(sub)
            taglist += set_taglist(t, {'base' : m.name})
        for sub in subs[1]:
            t = eval_content2(sub)
            taglist += set_taglist(t, {'sub' : m.name})
        return taglist
    else:
        return [tagtext(m.get_text(),  [{m.name : m.attrs}])]

def msup(m):
    sups = m.contents
    if len(sups) == 2:
        taglist = []
        for sup in sups[0]:
            t = eval_content2(sup)
            taglist += set_taglist(t, {'base' : m.name})
        for sup in sups[1]:
            t = eval_content2(sup)
            taglist += set_taglist(t, {'sup' : m.name})
        return taglist
    else:
        return [tagtext(m.get_text(),  [{m.name : m.attrs}])]    
    
def msubsup(m):
    subsups = m.contents
    if len(subsups) == 3:
        taglist = []
        for sbp in subsups[0]:
            t = eval_content2(sbp)
            taglist += set_taglist(t, {'base' : m.name}) 
        for sbp in subsups[1]:
            t = eval_content2(sbp)
            taglist += set_taglist(t, {'sub' : m.name}) 
        for sbp in subsups[2]:
            t = eval_content2(sbp)
            taglist += set_taglist(t, {'sup' : m.name})    
        return taglist
    else:
        return [tagtext(m.get_text(),  [{m.name : m.attrs}])]
    
    
def mfrac(m):
    mfracs = m.contents
    if len(mfracs) == 2:
        taglist = []
        for mfr in mfracs[0]:
            t = eval_content2(mfr)
            taglist += set_taglist(t, {'numerator' : m.name})                 
        for mfr in mfracs[1]:
            t = eval_content2(mfr)
            taglist += set_taglist(t, {'denominator' : m.name})                  
        return taglist
    else:
        return [tagtext(m.get_text(),  [{m.name : m.attrs}])]

    
def mmultiscripts(m):
    ind = [i for i, x in enumerate(m.contents) if x.name == 'mprescripts']
    taglist = []
    if len(ind):
        mmultis = m.contents[ind[0] + 1:] + m.contents[:ind[0]]  # reorder contents
        for i, mmulti in enumerate(mmultis):
            for mm in mmulti:
                if i == 2: 
                    ntag = 'base'
                else:
                    ntag = 'sub' if i in [0, 3, 5, 7, 9] else 'sup'
                t = eval_content2(mm)
                taglist += set_taglist(t, {ntag : m.name})
    else:
        print('chgeck mmultiscripts')
        for i, mm in enumerate(m):
            if i == 0:
                ntag = 'base'
            else:
                ntag = 'sub' if i in [2, 4, 6] else 'sup'
#             print(i, ntag, mm.name, mm)
            t = eval_content2(mm)
            taglist += set_taglist(t, {ntag : m.name})
    return taglist

                                                      
def msqrt(m):
    taglist = []
    for sqrt in m:
        t = eval_content2(sqrt)
        taglist += set_taglist(t, {m.name : m.attrs})
    return taglist

                                                      
def mroot(m):
    taglist = []
    t = eval_content2(m.contents[-1])
    taglist += set_taglist(t, {m.name : m.attrs})
    for root in m.contents[:-1]:
        t = eval_content2(root)
        taglist += set_taglist(t, {m.name : m.attrs})
    return taglist

                                                      
def menclose(m):
    taglist = []
    for enclose in m:
        t = eval_content2(enclose)
        taglist += set_taglist(t, {m.name : m.attrs})
    return taglist

                                                      
def mfenced(m):
    taglist = []
    if 'open' in m.attrs.keys():
        if m['open']:  # not ''
            taglist = [tagtext(m['open'], [{'open' : m.name}])]
    for fence in m:
        t = eval_content2(fence)
        taglist += set_taglist(t, {m.name : m.attrs})
    if 'close' in m.attrs.keys():
        if m['close']:  # not ''
            taglist += [tagtext(m['close'], [{'close' : m.name}])]
    return taglist

                                                      
# def ms(m):
# #     print(m.name, m.attrs, m.contents)
#     taglist = []
#     if 'lquote' in m.attrs.keys():
#         if m['lquote']:  # not ''
#             taglist = [tagtext(m['lquote'], [{m.name : m.attrs}])]
#     for s in m:
#         t = eval_content2(s)
#         taglist += set_taglist(t, {m.name : m.attrs})
#     if 'rquote' in m.attrs.keys():
#         if m['rquote']:  # not ''
#             taglist += [tagtext(m['rquote'], [{m.name : m.attrs}])]
#     return taglist

# for table tag maligngroup, mtd, mtr, mtable
def maligngroup(m):
    taglist = []
    for align in m.contents:
        t = eval_content2(align)
        taglist += set_taglist(t, {m.name : m.attrs})
    return taglist
    
    
def mtd(m):
    taglist = []
    for td in m.contents:
        t = eval_content2(td)
        taglist += set_taglist(t, {m.name : m.attrs})
    return taglist


def mtr(m):
    taglist = []
    for tr in m.contents:
        t = eval_content2(tr)
        taglist += set_taglist(t, {m.name : m.attrs})
    return taglist


def mtable(m):  # check required !
    taglist = []
    for table in m.contents:
        t = eval_content2(table)
        taglist += set_taglist(t, {m.name : m.attrs})
    return taglist     

                                                      
def mpadded(m):
    taglist = []
    for padded in m.contents:
        t = eval_content2(padded)
        taglist += set_taglist(t, {m.name : m.attrs})
    return taglist

                                                      
def mphantom(m):
    taglist = []
    for phantom in m.contents:
        t = eval_content2(phantom)
        taglist += set_taglist(t, {m.name : m.attrs})
    return taglist