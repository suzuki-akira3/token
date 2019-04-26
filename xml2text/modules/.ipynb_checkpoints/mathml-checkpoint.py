### mathML
### 上付き、下付きは一文字でも{}を付けることにした。

def my_index(l, x):
    return [i for i, _x in enumerate(l) if x in str(_x)]

def my_mmultiscripts(contents, l):
    # l=0:sub, l=1:sup
    ll = '^' if l else '_'
    if '<mml:none/>' in str(contents):
        return ''
    else:
        aa = contents.get_text()
        bb = '{0}{{{1}}}'.format(ll, aa)
        return bb
    
def get_mmultiscripts(mc):
    psub = psup = psub2 = psup2 = ''
    sub1 = sup1 = sub2 = sup2 = sub3 = sup3 = '' 
    
    ### base
    base = mc[0].get_text()

    ### prescript　あり、無しで形式が異なる
    ind = my_index(mc, '<mml:mprescripts/>')
    # mprescriptがある場合
    if ind:
        if ind[0] > 2: # mprescriptの前にsub,supがある場合
            sub1 = my_mmultiscripts(mc[1], 0) # post-sub
            sup1 = my_mmultiscripts(mc[2], 1) # post-sup 
        psub = my_mmultiscripts(mc[ind[0]+1], 0) # pre-sub
        psup = my_mmultiscripts(mc[ind[0]+2], 1) # pre-sup

        if len(mc) > ind[0]+3:
            psub2 = my_mmultiscripts(mc[ind[0]+3], 0) # next-post-sub
        if len(mc) > ind[0]+4:                
            psup2 = my_mmultiscripts(mc[ind[0]+4], 1) # next-post-sup

#             print('-\t{:<15} ->\t{:<15}'.format(b.get_text(), psub + psup + psub2 + psup2 + base + sub1 + sup1))
        return str(psub + psup + psub2 + psup2 + base + sub1 + sup1)

        # mprescriptが無い場合
    else:
        sub1 = my_mmultiscripts(mc[1], 0) # post-sub
        sup1 = my_mmultiscripts(mc[2], 1) # post-sup            
        if len(mc) > 3:
            sub2 = my_mmultiscripts(mc[3], 0) # next-post-sub
        if len(mc) > 4:    
            sup2 = my_mmultiscripts(mc[4], 1) # next-post-sup
        if len(mc) > 5:
             sub3 = my_mmultiscripts(mc[5], 0) # next-next-post-sub
        if len(mc) > 6:
            sup3 = my_mmultiscripts(mc[6], 1) # next-next-post-sup 

#             print(' \t{:<15} ->\t{:<15}'.format(b.get_text(), base + sub1 + sup1 + sub2 + sup2 + sub3 + sup3))
        return str(base + sub1 + sup1 + sub2 + sup2 + sub3 + sup3)  

def math_msub(formula):
    for sub in formula(re.compile(r'msub$')):
        if len(sub.contents) == 2: # 10.1063_1.1825632_jats.xmlでエラーのため
#             if sub.contents[0].string:
#                 sub.contents[0].string += '_'
#             elif sub.contents[0].name == 'mrow':
#                 sub.contents[0].string = sub.contents[0].get_text()    # '{' + sub.contents[0].get_text() + '}_'
#             elif sub.contents[0] == '<mrow/>':
#                 sub.contents[0].string == '_'
#             else:
#                 sub.contents[0].string = sub.contents[0].get_text() + '_' 
            #
            if sub.contents[1].string is not None:
#                 if len(sub.contents[1].string) >1:
                sub.contents[1].string = '_{' + sub.contents[1].string + '}' 
            elif sub.contents[1].name == 'mrow':
                sub.contents[1].string = '_{' + sub.contents[1].get_text() + '}'                
        else: 
            print('msub error: ', sub,  sub.contents)
            print(sub.parent)

def math_msup(formula):
    for sup in formula('msup'):
        if len(sup.contents) == 2:
#             if sup.contents[0].string:
#                 sup.contents[0].string += '^'
#             elif sup.contents[0].name == 'mrow':
#                 sup.contents[0].string = sup.contents[0].get_text() # '{' + sup.contents[0].get_text() + '}^'
            ### msupの中にmsubがある場合
#             elif sup.contents[0].name == 'msub':
            if sup.contents[0].name == 'msub': ## modified 20190306
                sup.contents[0].string = sup.msub.contents[0].get_text() + '_{' + sup.msub.contents[1].get_text() + '}^'

#                 if len(sup.msub.contents[1].get_text()) >1:
#                     sup.contents[0].string = sup.msub.contents[0].get_text() + '_{' + sup.msub.contents[1].get_text() + '}^'
#                 else:
#                     sup.contents[0].string = sup.msub.contents[0].get_text() + '_' + sup.msub.contents[1].get_text() + '^'
                sup.msub.unwrap()
#             else:
#                 sup.contents[0].string = sup.contents[0].get_text() + '^'
            if sup.contents[1].string is not None:
#                 if len(sup.contents[1].string) >1:
                sup.contents[1].string = '^{' + sup.contents[1].string + '}'
            elif sup.contents[1].name == 'mrow':
                sup.contents[1].string = '^{' + sup.contents[1].get_text() + '}'   
        else: 
            print('msup error: ', sup, sup.contents)    