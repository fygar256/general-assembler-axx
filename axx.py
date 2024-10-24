#!/usr/bin/python3

#
# axx general assembler designed and programmed by Taisuke Maekawa
#

import string as str
import itertools
import struct
import sys
import os
import re
EXP_PAT=0
EXP_ASM=1
OB=chr(0x90)     # open double bracket
CB=chr(0x91)     # close double bracket
UNDEF=0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff
VAR_UNDEF=0
capital="ABCDEFGHIJKLMNOPQRSTUVWXYZ"
lower="abcdefghijklmnopqrstuvwxyz"
ealphabet="abcdefg"
falphabet="hijklmn"
salphabet="opqrstuvwxyz"
digit='0123456789'
xdigit="0123456789ABCDEF"
outfile=""
expfile=""
impfile=""
pc=0
padding=0
alphabet=lower+capital
lwordchars=digit+alphabet+"_"
swordchars=digit+alphabet+"_%$-~&|"
symbols={}
labels={}
global_labels={}
pat=[]
expmode=EXP_PAT
error_undefined_label=False
align=32
pas=1
debug=0
cl=""
ln=0
current_file=""
fnstack=[]
lnstack=[]
vars=[ VAR_UNDEF for i in range(26) ]
deb1=""
deb2=""


def upper(o):
    t=""
    idx=0
    while len(o)>idx:
        a=o[idx]
        if a in lower:
            a=o[idx].upper()
        t+=a
        idx+=1
    return t

def outbin(a,x):
    if pas==2:
        x=int(x)&0xff
        print(" 0x%02x" % x,end='')
        if outfile!="":
            fwrite(outfile,a,x)

def get_vars(s):
    c=ord(upper(s))
    return vars[c-ord('A')]

def put_vars(s,v):
    global vars
    c=ord(upper(s))
    vars[c-ord('A')]=int(v)
    return

def q(s,t,idx):
    return upper(s[idx:idx+len(t)])==upper(t)

def err(m):
    print(m)
    return -1

def nbit(l):
    b=0
    r=l
    while(r):
        r>>=1
        b+=1
    return b

def skipspc(s,idx):
    while len(s)>idx:
        if s[idx]==' ':
            idx+=1
            continue
        break
    return idx

def get_param_to_spc(s,idx):
    t=""
    idx=skipspc(s,idx)
    while len(s)>idx:
        if s[idx]==' ':
            break
        t+=s[idx]
        idx+=1
    return t,idx

def get_param_to_eol(s,idx):
    t=""
    idx=skipspc(s,idx)
    while len(s)>idx:
        t+=s[idx]
        idx+=1
    return t,idx

def factor(s,idx):
    x=0
    if s[idx]=='-':
        (x,idx)=factor(s,idx+1)

    elif s[idx]=='~':
        (x,idx)=factor(s,idx+1)
        x=~x
    elif s[idx]=='@':
        (x,idx)=factor(s,idx+1)
        x=nbit(x)
    else:
        (x,idx)=factor1(s,idx)
    return (x,idx)

def getdicval(dic,k):
    k=k.upper()
    l=list(dic.keys())
    for i in l:
        if i==k:
            return dic[k]
    return UNDEF

def factor1(s,idx):
    global error_undefined_label
    x = 0

    idx=skipspc(s,idx)

    if s[idx]=='(':
        (x,idx)=expression(s,idx+1)
        if s[idx]==')':
            idx+=1
    elif q(s,'$$',idx):
        idx+=2
        x=pc
    elif q(s,'#',idx):
        idx+=1
        (t,idx)=get_symbol_word(s,idx)
        x=getsymval(t)

    elif q(s,'0b',idx):
        idx+=2
        while s[idx] in "01":
            x=2*x+int(s[idx],2)
            idx+=1

    elif q(s,'0x',idx):
        idx+=2
        while(upper(s[idx]) in xdigit):
            x=16*x+int(s[idx].lower(),16)
            idx+=1

    elif q(s,'0d',idx):
        idx+=2
        fs=''
        while(s[idx] in "0123456789.e"):
            fs+=s[idx]
            idx+=1
        x=int.from_bytes(struct.pack('>d',float(fs)),"little")

    elif q(s,'0f',idx):
        idx+=2
        fs=''
        while(s[idx] in "0123456789.e"):
            fs+=s[idx]
            idx+=1
        x=int.from_bytes(struct.pack('>f',float(fs)),"little")

    elif s[idx].isdigit():
        while(s[idx].isdigit()):
            x=10*x+int(s[idx])
            idx+=1
    elif expmode==EXP_PAT and s[idx] in lower:
        ch=s[idx]
        if s[idx+1:idx+3]==':=':
            (x,idx)=expression(s,idx+3)
            put_vars(ch,x)
        else:
            x=get_vars(ch)
            idx+=1
    else:
        if expmode==EXP_ASM and (s[idx] in lwordchars or s[idx]=='.'):
            w,idx_new=get_label_word(s,idx)
            w=w.upper()
            if idx!=idx_new:
                idx=idx_new
                if s[idx]==':':
                    idx+=1
                else:
                    pass
                x=getdicval(labels,w)
                if pas==2:
                    if x==UNDEF:
                        error_undefined_label=True
                    else:
                        error_undefined_label=False
                else:
                    pass
            else:
                pass
        else:
            pass
        idx=skipspc(s,idx)
    return (x,idx)

def term0_0(s,idx):
    (x,idx)=factor(s,idx)
    while True:
        if q(s,'**',idx):
            (t,idx)=factor(s,idx+2)
            x=x**t
        else:
            break
    return(x,idx)

def term0(s,idx):
    (x,idx)=term0_0(s,idx)
    while True:
        if (s[idx]=='*'):
            (t,idx)=term0_0(s,idx+1)
            x*=t
        elif q(s,'//',idx):
            (t,idx)=term0_0(s,idx+2)
            if t==0:
                err("Division by 0 error.")
            else:
                x//=t
        elif s[idx]=='%':
            (t,idx)=term0_0(s,idx+1)
            if t==0:
                err("Division by 0 error.")
            else:
                x=x%t
        else:
            break
    return (x,idx)

def term1(s,idx):
    (x,idx)=term0(s,idx)
    while True:
        if (s[idx]=='+'):
            (t,idx)=term0(s,idx+1)
            x+=t
        elif (s[idx]=='-'):
            (t,idx)=term0(s,idx+1)
            x-=t
        else:
            break
    return (x,idx)

def term2(s,idx):
    (x,idx)=term1(s,idx)
    while True:
        if q(s,'<<',idx):
            (t,idx)=term1(s,idx+2)
            x<<=t
        elif q(s,'>>',idx):
            (t,idx)=term1(s,idx+2)
            x>>=t
        else:
            break
    return (x,idx)

def term3(s,idx):
    (x,idx)=term2(s,idx)
    while True:
        if (s[idx]=='&' and s[idx+1]!='&'):
            (t,idx)=term2(s,idx+1)
            x=int(x)&int(t)
        else:
            break
    return (x,idx)


def term4(s,idx):
    (x,idx)=term3(s,idx)
    while True:
        if (s[idx]=='|' and s[idx+1]!='|'):
            (t,idx)=term3(s,idx+1)
            x=int(x)|int(t)
        else:
            break
    return (x,idx)

def term5(s,idx):
    (x,idx)=term4(s,idx)
    while True:
        if (s[idx]=='^'):
            (t,idx)=term4(s,idx+1)
            x=int(x)^int(t)
        else:
            break
    return (x,idx)

def term6(s,idx):
    (x,idx)=term5(s,idx)
    while True:
        if (s[idx]=='\''):
            (t,idx)=term5(s,idx+1)
            x=(x&~((~0)<<t))|((~0)<<t if (x>>(t-1)&1) else 0)
        else:
            break
    return (x,idx)

def term7(s,idx):
    (x,idx)=term6(s,idx)
    while True:
        if q(s,'<=',idx):
            (t,idx)=term6(s,idx+2)
            x=x<=t
        elif (s[idx]=='<'):
            (t,idx)=term6(s,idx+1)
            x=x<t
        elif q(s,'>=',idx):
            (t,idx)=term6(s,idx+2)
            x=x>=t
        elif (s[idx]=='>'):
            (t,idx)=term6(s,idx+1)
            x=x>t
        elif q(s,'==',idx):
            (t,idx)=term6(s,idx+2)
            x=x==t
        elif q(s,'!=',idx):
            (t,idx)=term6(s,idx+2)
            x=x!=t
        else:
            break
    return (x,idx)

def term8(s,idx):
    if s[idx:idx+4]=='not(':
        (x,idx)=expression(s,idx+3)
        if s[idx]==')':
            idx+=1
        x=not x
    else:
        (x,idx)=term7(s,idx)
    return (x,idx)

def term9(s,idx):
    (x,idx)=term8(s,idx)
    while True:
        if q(s,'&&',idx):
            (t,idx)=term8(s,idx+2)
            x=x and t
        else:
            break
    return (x,idx)

def term10(s,idx):
    (x,idx)=term9(s,idx)
    while True:
        if q(s,'||',idx):
            (t,idx)=term9(s,idx+2)
            x=x or t
        else:
            break
    return (x,idx)


def expression(s,idx):
    s+=chr(0)
    (x,idx)=term10(s,idx)
    return (x,idx)

def expression0(s,idx):
    global expmode
    expmode=EXP_PAT
    t,i=expression(s,idx)
    return (t,i)

def expression1(s,idx):
    global expmode
    expmode=EXP_ASM
    t,i=expression(s,idx)
    return (t,i)

def getsymval(w):
    w=w.upper()
    l=list(symbols.items())
    for i in l:
        if i[0]==w:
            return symbols[w]
    return "" 

def readfile(fn):
    f=open(fn,"rt")
    af=f.readlines()
    f.close()
    return af
    
def clear_symbol(i):
    global symbols
    if len(i)==0:
        return False
    if i[0]!='.clearsym':
    	return False
    symbols={}
    return True

def set_symbol(i):
    global symbols
    if len(i)==0:
        return False
    if i[0]!='.setsym':
    	return False
    key=upper(i[1])
    if len(i)>2:
        v,idx=expression0(i[2],0)
    else:
        v=0
    symbols[key]=v
    return True

def paddingp(i):
    global padding
    if len(i)==0:
        return False
    if len(i)>1 and i[0]!='.padding':
    	return False
    if len(i)>3:
        v,idx=expression0(i[2],0)
    else:
        v=0
    padding=int(v)
    return True

def labelc(i):
    global lwordchars
    if len(i)==0:
        return False
    if len(i)>1 and i[0]!='.labelc':
    	return False
    if len(i)>3:
        lwordchars=alphabet+digit+i[2]
    return True

def symbolc(i):
    global swordchars
    if len(i)==0:
        return False
    if len(i)>1 and i[0]!='.symbolc':
    	return False
    if len(i)>3:
        swordchars=alphabet+digit+i[2]
    return True

def remove_comment(l):
    idx=0
    while idx<len(l):
        if len(l[idx:])>2 and l[idx:idx+2]=='/*':
            if idx==0:
                return ""
            else:
                return l[0:idx-1]
        idx+=1
    return l

def remove_comment_asm(l):
    if ';' in l:
        s=l[0:l.index(';')]
    else:
        s=l
    return s.rstrip()

def get_params1(l,idx):
    idx=skipspc(l,idx)

    if idx>=len(l):
        return ("",idx)

    s=""
    while idx<len(l):
        if '::'==l[idx:idx+2]:
            idx+=2
            break
        else:
            s+=l[idx]
            idx+=1
    return(s.rstrip(' \t'),idx)

def reduce_spaces(text):
    return re.sub(r'\s{2,}', ' ', text)

def readpat(fn):
    if fn=='':
        return []
    f=open(fn,"rt")

    p=[]
    w=[]
    while(l:=f.readline()):
        l=remove_comment(l)
        l=l.replace('\t',' ')
        l=l.replace(chr(13),'')
        l=l.replace('\n','')
        l=reduce_spaces(l)
        ww=include_pat(l)
        if ww:
            w=w+ww
            continue
        else:
            r=[]
            idx=0
            while True:
                s,idx=get_params1(l,idx)
                r+=[s]
                if len(l)<=idx:
                    break
            l=r
            prev=l[0]
            l=[_ for _ in l if _]
            idx=0
            if len(l)==1:
                p=[l[0],'','']
            elif len(l)==2:
                p=[l[0],'',l[1]]
            elif len(l)==3:
                p=[l[0],l[1],l[2]]
            else:
                p=["","",""]
            w.append(p)

    f.close()
    return w

def fwrite(file_path, position, x):
    with open(file_path, 'r+b') as file:
        file.seek(0, 2)
        file_length = file.tell()
        if position > file_length:
            file.seek(file_length)
            for i in range(position-file_length):
                file.write(struct.pack("B",padding))
            # file.write(f"{padding:#b}" * (position - file_length))
        file.seek(position)
        file.write(struct.pack('B',x))

def align_(addr):
    a=addr%align
    if a==0:
        return addr
    addr+=align-a
    return addr

def pad(addr):
    npc=align_(addr)
    for i in range(addr,npc):
        outbin(i,padding)
    return npc-addr

def makeobj(s):
    s+=chr(0)
    idx=0
    cnt=0
    if pas==2:
        printaddr(pc)
        print(f"{current_file} {ln} {cl} " ,end='')
    while True:
        if s[idx]==chr(0):
            break
        if s[idx]==',':
            idx+=1
            cnt+=pad(pc+cnt)
            continue

        semicolon=False
        if s[idx]==';':
            semicolon=True
            idx+=1
        (x,idx)=expression0(s,idx)

        if pas==2 and ((semicolon==True and x!=0) or (semicolon==False)):
            outbin(pc+cnt,x)
        cnt+=1
        if s[idx]==',':
            idx+=1
            continue
        break

    if pas==2:
        print("")
    return cnt

def isword(s,idx):
    t,idx_s=getword(s,idx)
    if idx_s==idx:
        return False
    return True

def get_symbol_word(s,idx):
    t=""
    if len(s)>idx and (s[idx]=='.' or not s[idx] in digit and s[idx] in swordchars):
        t=s[idx]
        idx+=1
        while len(s)>idx:
            if not s[idx] in swordchars : 
                break
            t+=upper(s[idx])
            idx+=1
    return t,idx

def get_label_word(s,idx):
    t=""
    if len(s)>idx and (s[idx]=='.' or not s[idx] in digit and s[idx] in lwordchars):
        t=s[idx]
        idx+=1
        while len(s)>idx:
            if not s[idx] in lwordchars : 
                break
            t+=upper(s[idx])
            idx+=1
    return t.upper(),idx

def match(s,t):
    global deb1,deb2
    t=t.replace(OB,'').replace(CB,'')
    idx_s=0
    idx_t=0
    idx_s=skipspc(s,idx_s)
    idx_t=skipspc(t,idx_t)
    s+=chr(0)
    t+=chr(0)
    deb1=s
    deb2=t
    while True:
        idx_s=skipspc(s,idx_s)
        idx_t=skipspc(t,idx_t)
        b=s[idx_s] # bはアセンブリライン
        a=t[idx_t] # aはパターンファイル
        if a==chr(0) and b==chr(0):
            return True
        if a==chr(0x5c):
            idx_t+=1
            if upper(t[idx_t])==upper(b):
                idx_t+=1
                idx_s+=1
                continue
            else:
                return False
        elif a==b:
            idx_t+=1
            idx_s+=1
            continue
        elif a.isupper():
            if a==upper(b):
                idx_s+=1
                idx_t+=1
                continue
            else:
                return False
        elif a in falphabet:
              idx_t+=1
              (v,idx_s)=factor(s,idx_s)
              put_vars(a,v)
        elif a in ealphabet:
              idx_t+=1
              (v,idx_s)=expression1(s,idx_s)
              put_vars(a,v)
              continue
        elif a in salphabet:
              idx_t+=1
              (w,idx_s)=get_symbol_word(s,idx_s)
              v=getsymval(w)
              if (v==""):
                  return False
              put_vars(a,v)
              continue
        else:
              return False

def remove_brackets(s, l):
    open_count = 0
    result = list(s)
    
    # 開き大括弧と閉じ大括弧の位置を記録
    bracket_positions = []
    
    for i, char in enumerate(s):
        if char == OB:
            open_count += 1
            bracket_positions.append((open_count, i, 'open'))
        elif char == CB:
            bracket_positions.append((open_count, i, 'close'))
    
    # 指定されたインデックスの開き大括弧から閉じ大括弧までを削除
    for index in sorted(l, reverse=True):
        start_index = None
        end_index = None
        for count, pos, type in bracket_positions:
            if count == index and type == 'open':
                start_index = pos
            elif count == index and type == 'close':
                end_index = pos
                break
        
        if start_index is not None and end_index is not None:
            for j in range(start_index, end_index + 1):
                result[j] = ''
    
    return ''.join(result)


def match0(s,t):
    t=t.replace('[[',OB).replace(']]',CB)
    cnt=t.count(OB)
    sl=[ _+1 for _ in range(cnt) ]
    for i in range(len(sl)+1):
        ll=list(itertools.combinations(sl,i))
        for j in ll:
            lt=remove_brackets(t,list(j))
            if match(s,lt):
                return True
    return False
        
def error(s):
    ch=','
    s+=chr(0)
    idx=0
    error_occured=False
    while (ch:=s[idx])!=chr(0):
        if ch==',':
            idx+=1
            continue
        u,idx=expression0(s,idx)
        if s[idx]==';':
            idx+=1
        t,idx=expression0(s,idx)
        if pas==2 and u:
            print(f"error code : {t}")
            error_occured=True

    return error_occured

def label_processing(l):
    if l=="":
        return ""
    label,idx=get_label_word(l,0)
    if len(l)>idx and l[idx]==':':
        idx+=1
        if pas==2 and len(label)<2:
            print("Label too short")
            return "" 
        idx=skipspc(l,idx)
        idx1=idx
        e,idx=get_param_to_spc(l,idx)
        if upper(e)=='.EQU':
            idx=skipspc(l,idx)
            s=l.replace(' ','')
            u,idx=expression1(l,idx)
            labels[label.upper()]=u
            return ""
        else:
            labels[label.upper()]=pc
            return l[idx1:]
    else:
        return l

def get_string(l2):
    idx=0
    idx=skipspc(l2,idx)
    if l2=='' or l2[idx]!='"':
        return ""
    idx+=1
    s=""
    while idx<len(l2):
        if l2[idx]=='"':
            return s
        else:
            s+=l2[idx]
            idx+=1
    return s

def asciistr(l2):
    global pc
    idx=0
    if l2=='' or l2[idx]!='"':
        return False
    idx+=1
    while idx<len(l2):
        if l2[idx]=='"':
            return True
        if l2[idx:idx+2]=='\\0':
            idx+=2
            ch=chr(0)
        elif l2[idx:idx+2]=='\\t':
            idx+=2
            ch='\t'
        elif l2[idx:idx+2]=='\\n':
            idx+=2
            ch='\n'
        else:
            ch=l2[idx]
            idx+=1
        outbin(pc,ord(ch))
        pc+=1

def global_processing(l1,l2):
    if upper(l1)!=".GLOBAL":
        return False

    idx=0
    l2+=chr(0)
    while l2[idx]!=chr(0):
        idx=skipspc(l2,idx)
        s,idx=get_label_word(l2,idx)
        if s=="":
            break
        if l2[idx]==':':
            idx+=1
        v=getdicval(labels,s)
        if pas==2 and v==UNDEF:
            error_label_undefined=True
            break
        global_labels[s]=v
        if l2[idx]==',':
            idx+=1
    return True

def ascii_processing(l1,l2):
    if upper(l1)!=".ASCII":
        return False

    f=asciistr(l2)
    if pas==2:
        print("")
    return(f)

def asciiz_processing(l1,l2):
    global pc
    if upper(l1)!=".ASCIIZ":
        return False
    f=asciistr(l2)
    if f:
        outbin(pc,0x00)
        pc+=1
    if pas==2:
        print("")
    return True

def include_pat(l):
    idx=skipspc(l,0)
    i=l[idx:idx+8]
    i=i.upper()
    if i!=".INCLUDE":
        return []
    s=get_string(l[8:])
    w=readpat(s)
    return w

def include_asm(l1,l2):
    if upper(l1)!=".INCLUDE":
        return False
    s=get_string(l2)
    if s:
        fileassemble(s)
    return True

def align_processing(l1,l2):
    global pc,align

    if upper(l1)!=".ALIGN":
        return False

    if l2!='':
        u,idx=expression1(l2,0)
        align=int(u)

    pc=align_(pc)
    return True

def printaddr(pc):
    print("%016x: " % pc,end='')

def org_processing(l1,l2):
    global pc
    if upper(l1)!=".ORG":
        return False
    u,idx=expression1(l2,0)
    pc=u
    return True

def lineassemble(line):
    global pc,cl,ln,error_undefined_label
    ln+=1
    error_undefined_label=False
    cl=line.replace('\n','')
    line=line.replace('\t',' ').replace('\n','')
    line=reduce_spaces(line)
    line=remove_comment_asm(line)
    if line=='':
        return False
    line=label_processing(line)
    (l,idx)=get_param_to_spc(line,0)
    (l2,idx)=get_param_to_eol(line,idx)
    l=l.rstrip()
    l2=l2.rstrip()
    l=l.replace(' ','')
    ll2=l2.replace(' ','')
    if ascii_processing(l,l2):
        return True
    if asciiz_processing(l,l2):
        return True
    if include_asm(l,l2):
        return True
    l=l.upper()
    l2=l2.upper()
    ll2=ll2.upper()
    if align_processing(l,ll2):
        return True
    if org_processing(l,ll2):
        return True
    if global_processing(l,ll2):
        return True
    if  l=="":
        return False
    idx=0
    of=0
    se=False
    for i in pat:
        for a in lower:
            put_vars(a,VAR_UNDEF)
        #
        # i はパターンファイルのデータ
        # l はアセンブリライン
        #
        if i is None: continue
        if set_symbol(i): continue
        if clear_symbol(i): continue
        if paddingp(i): continue
        if symbolc(i): continue
        if labelc(i): continue
        lw=len([_ for _ in i if _])
        if lw==0:
            continue
        lin=l+' '+l2
        lin=reduce_spaces(lin)
        if i[0]=='':
            break
        if match0(lin,i[0])==True:
            if lw==3:
                if error(i[1]):
                    of = 0
                    break
                else:
                    of=makeobj(i[2])
                    break
            else:
                of=makeobj(i[2])
                break
    else:
        se=True

    pc+=of
    if pas==2:
        if error_undefined_label==True:
            print(f"{current_file} : {ln} : {cl} : undefined label error.")
            return False
        elif se:
            print(f"{current_file} : {ln} : {cl} : error.")
            return False
    return True

def option(l,o):
    if o in l:
        idx=l.index(o)
        if idx+1<len(l):
            if idx+2<len(l):
                return l[0:idx]+l[idx+2:],l[idx+1]
            else:
                return l[0:idx],l[idx+1]
        else:
            return l[0:idx],''
    return l,''

def fileassemble(fn):
    global current_file,fnstack,lnstack,ln
    
    fnstack+=[current_file]
    lnstack+=[ln]
    current_file=fn
    ln=0
    f=open(fn,"rt")
    af=f.readlines()
    for i in af:
        lineassemble(i)
    f.close()
    if fnstack:
        current_file=fnstack.pop()
        ln=lnstack.pop()

def imp_label(l):
    global labels
    idx=skipspc(l,0)
    (label,idx)=get_label_word(l,idx)
    if label=='':
        return False
    idx=skipspc(l,idx)
    (v,new_idx)=expression(l,idx)
    if new_idx==idx:
        return False
    idx=new_idx
    labels[label.upper()]=v
    return True

def main():
    global pc,pas,ln,outfile,expfile,impfile,current_file,pat

    if len(sys.argv)==1:
        print("axx general assembler programmed and designed by Taisuke Maekawa")
        print("Usage: python axx.py patternfile.axx [sourcefile.s] [-o outfile.bin] [-l export_labels.tsv] [-i import_labels.tsv]")
        return

    sys_argv=sys.argv

    if len(sys_argv)>=2:
        pat=readpat(sys_argv[1])

    (sys_argv,expfile)=option(sys_argv,"-e")
    (sys_argv,outfile)=option(sys_argv,'-o')
    (sys_argv,impfile)=option(sys_argv,"-i")

#
# import labels from file
#
    if impfile!="":
        with open(impfile,"rt") as label_file:
            while (l:=label_file.readline()):
                imp_label(l)

    try:
        os.remove(outfile)
    except:
        pass
    else:
        pass
    if outfile:
        f=open(outfile,"wb")
        f.close()
    if len(sys_argv)==2:
        pc=0
        pas=2
        ln=0
        current_file="(stdin)"
        while True:
            printaddr(pc)
            try:
                line=input(">> ")
                line=line.replace("\\\\","\\")
            except EOFError: # EOF
                break
            lineassemble(line)

    elif len(sys_argv)>=3:
        pc=0
        pas=1
        ln=0
        fileassemble(sys_argv[2])
        pc=0
        pas=2
        ln=0
        fileassemble(sys_argv[2])

    if expfile!="":
        h=list(global_labels.items())
        with open(expfile,"wt") as label_file:
            for i in h:
                label_file.write(f"{i[0]}\t{i[1]}\n")

if __name__=='__main__':
    main()
    exit(0)
