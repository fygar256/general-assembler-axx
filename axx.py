#!/usr/bin/python3

#
# axx general assembler designed and programmed by Taisuke Maekawa
#

import string as str
import struct
import sys
import os
import re
UNDEF = (~(0))
EXP_PAT=0
EXP_ASM=1
LV_UNDEF=0
capital="ABCDEFGHIJKLMNOPQRSTUVWXYZ"
lower="abcdefghijklmnopqrstuvwxyz"
ealphabet="abcdefg"
falphabet="hijklmn"
salphabet="opqrstuvwxyz"
digit='0123456789'
xdigit="0123456789ABCDEF"
outfile=""
pc=0
padding=0
alphabet=lower+capital
wordchars=digit+alphabet+"_"+"%$-~&|"
symbols={}
labels={}
pat=[]
expmode=EXP_PAT
pas=1
debug=0
cl=""
ln=0
vars=[ LV_UNDEF for i in range(26) ]

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
        (t,idx)=getword(s,idx)
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
        if expmode==EXP_ASM and (s[idx] in wordchars or s[idx]=='.'):
            w,idx=getword(s,idx)
            if issymbol(w)==False:
                x=getdicval(labels,w)
                if pas==2 and x==UNDEF:
                    print(f"{ln} : {cl} : Undefined label")
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
            idx+=2
            (t,idx)=term0_0(s,idx)
            if t==0:
                err("Division by 0 error.")
            else:
                x//=t
        elif s[idx]=='%':
            (t,idx)=term0_0(s,idx+1)
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
    l=list(symbols.items())
    for i in l:
        if i[0]==w:
            return symbols[w]
    return "" 

def issymbol(w):
    l=list(symbols.items())
    for i in l:
        if i[0]==w:
            return w
    return False
    
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
    if len(i)==0:
        return False
    if len(i)>1 and i[0]!='.setsym':
    	return False
    if len(i)>3:
        v,idx=expression0(i[3],0)
    else:
        v=-1
    key=upper(i[1])
    symbols[upper(key)]=v
    return True

def paddingp(i):
    global padding
    if len(i)==0:
        return False
    if len(i)>1 and i[0]!='.padding':
    	return False
    if len(i)>3:
        v,idx=expression0(i[3],0)
    else:
        v=0
    padding=int(v)
    return True

def wordc(i):
    global etc 
    if len(i)==0:
        return False
    if not i[0]=='.wordc':
        return False
    p=i[3]
    s=chr(0)
    idx=0
    while idx<len(p):
        s+=p[idx]
        idx+=1
    wordc=s
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
        return l[0:l.index(';')]
    return l

def get_params1(l,idx):
    idx=skipspc(l,idx)
    if len(l)<=idx:
        return ("",idx)
    if not l[idx]=='\"':
        idx=skipspc(l,idx)
        return get_param_to_spc(l,idx)
    s=""
    idx+=1
    while True:
        if '\"'==l[idx]:
            idx+=1
            break
        s+=l[idx]
        idx+=1
    return (s,idx)

def reduce_spaces(text):
    return re.sub(r'\s{2,}', ' ', text)

def readpat(fn):
    global pat
    f=open(fn,"rt")
    p=[]
    w=[]
    prev=''
    while(l:=f.readline()):
        l=remove_comment(l)
        l=l.replace('\t',' ')
        l=l.replace('\n','')
        l=reduce_spaces(l)
        r=[]
        idx=0
        if len(l)>1 and l[0]==' ':
            l=prev+" "+l
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
            p=[l[0],'','','']
        elif len(l)==2:
            p=[l[0],'','',l[1]]
        elif len(l)==3:
            p=[l[0],l[1],'',l[2]]
        elif len(l)==4:
            p=[l[0],l[1],l[2],l[3]]
        else:
            p=[]
        w.append(p)

    pat=w
    f.close()
    return

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

def makeobj(s):
    s+=chr(0)
    idx=0
    cnt=0
    if pas==2:
        print("%016x:" % pc,end='')
    while True:
        if s[idx]==chr(0):
            break
        (x,idx)=expression0(s,idx)
        if pas==2:
            x=int(x)&0xff
            print(" 0x%02x" % x,end='')
            if outfile!="":
                fwrite(outfile,pc+cnt,x)
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

def getword(s,idx):
    t=""
    if len(s)>idx and (s[idx]=='.' or not s[idx] in digit and s[idx] in wordchars):
        t=s[idx]
        idx+=1
        while len(s)>idx:
            if not s[idx] in wordchars : 
                break
            t+=upper(s[idx])
            idx+=1
    return t,idx

def match(s,t):
    idx_s=0
    idx_t=0
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
              (w,idx_s)=getword(s,idx_s)
              v=getsymval(w)
              if (v==""):
                  return False
              put_vars(a,v)
              continue
        else:
              return False

def remove_ookakko(t):
    if '[[' in t and ']]' in t:
        i = t.index('[[')
        c = t.index(']]')
        return t[0:i]+t[c+2:]
    return t
    

def match0(s,t):
    s+=chr(0)
    t+=chr(0)

    tt=remove_ookakko(t)
    if match(s,tt)==True:
        return True

    tt=t.replace('[[','').replace(']]','')
    if match(s,tt)==True:
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
    label,idx=getword(l,0)
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
            labels[label]=u
            return ""
        else:
            labels[label]=pc
            return l[idx1:]
    else:
        return l

def align_processing(l1,l2):
    global pc
    if upper(l1)!=".ALIGN":
        return False
    u,idx=expression1(l2,0)
    a=pc%int(u)
    pc+=(u-a)
    return True

def org_processing(l1,l2):
    global pc
    if upper(l1)!=".ORG":
        return False
    u,idx=expression1(l2,0)
    pc=u
    return True

def lineassemble(line):
    global pc,cl,ln
    ln+=1
    cl=line.replace('\n','')
    for a in lower:
        put_vars(a,LV_UNDEF)
    line=upper(line.replace('\t',' ').replace('\n',''))
    line=reduce_spaces(line)
    line=remove_comment_asm(line)
    if line=='':
        return False
    line=label_processing(line)
    (l,idx)=get_param_to_spc(line,0)
    (l2,idx)=get_param_to_eol(line,idx)
    l=l.replace(' ','')
    ll2=l2.replace(' ','')
    if align_processing(l,ll2):
        return True
    if org_processing(l,ll2):
        return True
    if  l=="":
        return False
    idx=0
    of=0
    se=False
    for i in pat:
        #
        # i はパターンファイルのデータ
        # l はアセンブリライン
        #
        if set_symbol(i): continue
        if clear_symbol(i): continue
        if wordc(i): continue
        if paddingp(i): continue
        lw=len([_ for _ in i if _])
        if lw==0:
            continue
        if match0(l,i[0])==True:
            if lw==1 or lw==2:
                of=makeobj(i[3])
                break
            elif lw==3:
                if match0(l2,i[1])==True:
                    of=makeobj(i[3])
                    break
            elif lw==4:
                if match0(l2,i[1])==True:
                    if error(i[2]):
                        of = 0
                        break
                    else:
                        of=makeobj(i[3])
                        break
    else:
        se=True
    if se and pas==2:
        print(f"{ln} : {cl} : Syntax error")
        return False
    pc+=of
    return True

def main():
    global pc,pas,ln,outfile

    if len(sys.argv)==1:
        print("axx general assembler programmed and designed by Taisuke Maekawa")
        print("Usage: python axx.py patternfile.axx [[sourcefile.s] outfile.bin")
        return

    ofs=0

    sys_argv=sys.argv
    if len(sys_argv)>=2+ofs:
        readpat(sys_argv[1+ofs])

    if len(sys_argv)>=4+ofs:
        outfile=sys.argv[3+ofs]
        try:
            os.remove(outfile)
        except:
            pass
        else:
            pass
        f=open(outfile,"wb")
        f.close()
    if len(sys_argv)==2+ofs:
        pc=0
        pas=2
        ln=0
        while True:
            print("%016x:" % pc,end='')
            try:
                line=input(">> ")
            except EOFError: # EOF
                break
            lineassemble(line)
    elif len(sys_argv)>=3+ofs:
        af=readfile(sys_argv[2+ofs])
        pc=0
        pas=1
        ln=0
        for i in af:
            lineassemble(i)
        pc=0
        pas=2
        ln=0
        for i in af:
            lineassemble(i)

if __name__=='__main__':
    main()
    exit(0)
