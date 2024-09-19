#!/usr/bin/python3

#
# axx general assembler designed and programmed by Taisuke Maekawa
#

import string as str
import struct
import sys
pc=0
capital="ABCDEFGHIJKLMNOPQRSTUVWXYZ"
lower="abcdefghijklmnopqrstuvwxyz"
nalphabet="abcdefghijklmn"
salphabet="opqrstuvwxyz"
digit='0123456789'
xdigit="0123456789ABCDEF"
etc='+-*/ .,;:()[]{}"\'\n\t'+chr(0)
alphabet=lower+capital
symbols={}
labels={}
pat=[]

vars=[ 0 for i in range(26) ]

def get_vars(s):
    c=ord(s.upper())
    return vars[c-ord('A')]

def put_vars(s,v):
    global vars
    c=ord(s.upper())
    vars[c-ord('A')]=int(v)
    return

def q(s,t,idx):
    return s[idx:idx+len(t)].upper()==t.upper()

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

def factor(s,idx):
    x=0
    if s[idx]=='-':
        (x,idx)=factor(s,idx+1)
        x=-x
    elif s[idx]=='~':
        (x,idx)=factor(s,idx+1)
        x=~x
    elif s[idx]=='@':
        (x,idx)=factor(s,idx+1)
        x=nbit(x)
    else:
        (x,idx)=factor1(s,idx)
    return (x,idx)

def factor1(s,idx):
    x = 0

    while True:
        if s[idx]==' ' or s[idx]=='\t':
            idx+=1
            continue
        break

    if q(s,'$$',idx):
        idx+=2
        x=pc
    elif q(s,'#',idx):
        idx+=1
        (t,idx)=getword(s,idx)
        x=getsymval(t)
    elif q(s,'0b',idx):
        idx+=2
        while(s[idx].upper() in "01"):
            x=2*x+(ord(s[idx])-0x30)
            idx+=1

    elif q(s,'0x',idx):
        idx+=2
        while(s[idx].upper() in xdigit):
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
    elif s[idx]=='!':
        t,idx=getword(s,idx+1)
        x=labels[t]
    elif s[idx].islower():
        ch=s[idx]
        if s[idx+1:idx+3]==':=':
            (x,idx)=expression(s,idx+3)
            put_vars(ch,x)
        else:
            x=get_vars(s[idx])
            idx+=1
    elif s[idx]=='(':
        (x,idx)=expression(s,idx+1)
        if s[idx]==')':
            idx+=1
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
        elif (s[idx]=='/'):
            (t,idx)=term0_0(s,idx+1)
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
    if s[idx:idx+4]=='not ':
        (x,idx)=term8(s,idx+3)
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

def getsymval(w):
    l=list(symbols.items())
    for i in l:
        if i[0]==w:
            return symbols[w]
    return 0 

def issymbol(w):
    l=list(symbols.items())
    for i in l:
        if i[0]==w:
            return w
    return ''
    
def readfile(fn):
    f=open(fn,"rt")
    af=f.readlines()
    f.close()
    return af
    
def set_symbol(i):
    if i[0]!='.setsym':
    	return False
    v,idx=expression(i[3],0)
    (symbols[i[1].upper()],idx) =(v,idx)
    return True

def termc(i):
    global etc 
    if len(i)==0:
        return False
    if not i[0]=='.termc':
        return False
    p=i[3]
    s=''
    idx=0
    while idx<len(p):
        if p[idx]=='\\':
            idx+=1
            if p[idx]=='n':
                s+='\n'
                idx+=1
            elif p[idx]=='\'':
                s+='\''
                idx+=1
            elif p[idx]=='t':
                s+='\t'
                idx+=1
            elif p[idx]=='0':
                s+=chr(0)
                idx+=1
        else:
            s+=p[idx]
            idx+=1
    etc=s
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

def replace_garbages(s):
    s=s.replace(chr(0),'')
    s=s.replace('\n',"")
    s=s.replace(chr(13),'')
    s=s.replace('\t','')
    s=s.replace(' ','')
    return(s)

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
        l=l.split(' ')

        if len(l)>0 and l[0]=="":
            l[0]=prev
        prev=l[0]
        l=[_ for _ in l if _]
        idx=0
        t=l

        if len(t)==1:
            p=[t[0],'','','']
        elif len(t)==2:
            p=[t[0],'','',t[1]]
        elif len(t)==3:
            p=[t[0],t[1],'',t[2]]
        elif len(t)==4:
            p=[t[0],t[1],t[2],t[3]]
        else:
            p=[]
        w.append(p)

    pat=w
    f.close()
    return

def makeobj(s):
    s+=chr(0)
    idx=0
    cnt=0
    while True:
        sidx=idx
        (x,idx)=expression(s,idx)
        if sidx!=idx:
            x=int(x)&0xff
            print("0x%02x," % x,end='')
            cnt+=1
        ch=s[idx]
        if ch==chr(0):
            break
        if ch==',':
            idx+=1
            continue
        break
    print("")
    return cnt

def isword(s,idx):
    t,idx_s=getword(s,idx)
    if idx_s==idx:
        return False
    return True

def getword(s,idx):
    t=""
    while len(s)>idx and not (s[idx] in etc):
        t+=s[idx].upper()
        idx+=1
    return t,idx
    
def match(s,t):
    s+=chr(0)
    t+=chr(0)
    idx_s=0
    idx_t=0
    while True:
        b=s[idx_s] # bはアセンブリライン
        a=t[idx_t] # aはパターンファイル
        if a==chr(0) and b==chr(0):
            return True
        elif a=='\\':
            idx_t+=1
            a=t[idx_t].upper()

        if a==b:
            idx_s+=1
            idx_t+=1
            continue
        elif a in digit:
            if b==a:
                idx_s+=1
                idx_t+=1
                continue
            else:
                return False

        elif a.isupper():
            if a==b.upper():
                idx_s+=1
                idx_t+=1
                continue
            else:
                return False
        elif a.islower():
          idx_t+=1
          if a in nalphabet:
            s_idx_s=idx_s
            (v,s_idx_s)=expression(s,idx_s)
            if idx_s==s_idx_s:
                return False
            else:
                idx_s=s_idx_s
                put_vars(a,v)
                continue
          elif a in salphabet:
                (w,s_idx_s)=getword(s,idx_s)
                if idx_s==s_idx_s:
                    return False
                idx_s=s_idx_s
                if issymbol(w.upper()):
                    put_vars(a,symbols[w.upper()])
                continue
        elif a!=b:
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

        u,idx=expression(s,idx)
        if s[idx]==';':
            idx+=1
        t,idx=expression(s,idx)
        if u:
            print(f"error code {t} ")
            error_occured=True

    return error_occured

def label_processing(l,l2,l3):
    t=l
    s,idx=getword(t,0)
    if len(t)==idx:
        return (l,l2,l3)
    if len(t)>idx and t[idx]==':':
        l=l2
        l2=l3
        l3=""

    if l.upper()=='EQU':
        u,idx=expression(l2,0)
        labels[s]=u
        return ("","","")
    else:
        labels[s]=pc
        return (l,l2,"")

def lineassemble(line):
    line=line.replace('\t','').replace('\n','').upper().split(' ')
    lin=[_ for _ in line if _]
    l=""
    l2=""
    l3=""
    if len(lin)>=1:
        l=lin[0]
    if len(lin)>=2:
        l2=lin[1]
    if len(lin)>=3:
        l3=lin[2]
    (l,l2,l3)=label_processing(l,l2,l3)
    if  l=="":
        return 0
    idx=0
    of=0
    se=False
    for i in pat:
        #
        # i はパターンファイルのデータ
        # l はアセンブリライン
        #
        if set_symbol(i): continue
        if termc(i): continue
        lw=len([_ for _ in i if _])
        if lw==0:
            continue
        if match(l,i[0]):
            if lw==1 or lw==2:
                of=makeobj(i[3])
                break
            elif lw==3:
                if match(l2,i[1]):
                    of=makeobj(i[3])
                    break
            elif lw==4:
                if match(l2,i[1]):
                    if error(i[2]):
                        of = 0
                        break
                    else:
                        of=makeobj(i[3])
                        break
    else:
        se=True
    if se:
        print("Syntax error")
    return of

def main():
    global pc
    pc=0

    if len(sys.argv)==1:
        print("axx general assembler programmed and designed by Taisuke Maekawa")
        print("Usage: python axx.py patternfile.axx [sourcefile.s]")
        return

        ofs=0

    sys_argv=sys.argv
    if len(sys_argv)>=2:
        readpat(sys_argv[1])

    if len(sys_argv)==2:
        while True:
            line=input(">> ")
            pc+=lineassemble(line)
    elif len(sys_argv)>=3:
        af=readfile(sys_argv[2])
        for i in af:
            pc+=lineassemble(i)

if __name__=='__main__':
    main()
    exit(0)
