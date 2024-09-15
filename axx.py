#!/usr/bin/python3

#
# axx general assembler designed and programmed by Taisuke Maekawa
#

import string
import struct
import sys
pc=0
capital="ABCDEFGHIJKLMNOPQRSTUVWXYZ"
lower="abcdefghijklmnopqrstuvwxyz"
digits='0123456789'
etc=' '+chr(0)+'\n'+'\t'+',;()[]{}\"\''
alphabet=lower+capital
debug=0
symbols={}
pat=[]

vars=[ 0 for i in range(26) ]

def get_vars(s):
    c=ord(s.upper())
    return vars[c-ord('A')]

def put_vars(s,v):
    global vars
    c=ord(s.upper())
    vars[c-ord('A')]=v
    return

q=lambda s,t,idx:(s[idx:idx+len(t)].upper()==t.upper())

def err(m):
    print(m)
    return -1

def factor(s,idx):
    x=0
    if s[idx]=='-':
        (x,idx)=factor(s,idx+1)
        x=-x
    elif s[idx]=='~':
        (x,idx)=factor(s,idx+1)
        x=~x
    elif q(s,'##',idx):
        (a,idx)=getword(s,idx+1)
        if issymbol(a):
            x=symbols[a]
    elif q(s,'#',idx):
        chara=s[idx+1]
        idx+=2
        x=get_vars(chara)
    else:
        (x,idx)=factor1(s,idx)
    return (x,idx)

def factor1(s,idx):
    x = 0

    if q(s,'$$',idx):
        idx+=2
        x=pc
    elif q(s,'0b',idx):
        idx+=2
        while(s[idx].upper() in "01"):
            x=2*x+(ord(s[idx])-0x30)
            idx+=1

    elif q(s,'0x',idx):
        idx+=2
        while(s[idx].upper() in "0123456789ABCDEF"):
            x=16*x+int(s[idx],16)
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

    elif s[idx] in digits:
        while(s[idx] in digits):
            x=10*x+ord(s[idx])-0x30
            idx+=1
        a=1
        if (s[idx]=='.'):
            idx+=1
            while(s[idx] in digits):
                x+=(a/10)*(ord(s[idx])-0x30)
                a/=10
                idx+=1

    elif s[idx] in lower:
        x=vars[ord(s[idx].upper())-0x41]
        idx+=1
    elif s[idx]=='(':
        (x,idx)=expression(s,idx+1)
        if s[idx]!=')':
            err("Missing ')'.")
            idx=-1
        else:
            idx+=1
    return (x,idx)

def term0(s,idx):
    (x,idx)=factor(s,idx)
    while True:
        if (s[idx]=='*'):
            (t,idx)=factor(s,idx+1)
            x*=t
        elif (s[idx]=='/'):
            (t,idx)=factor(s,idx+1)
            if t==0:
                err("Division by 0 error.")
                idx=-1
                x=-1
            else:
                x//=t
        elif s[idx]=='%':
            (t,idx)=factor(s,idx+1)
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
    if s[idx]=='!':
        (x,idx)=term8(s,idx+1)
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
    return term10(s,idx)

def getsymval(w):
    l=list(symbols.items())
    for i in l:
        if i[0]==w:
            return w
    return ''

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
    if not i:
        return False
    if not i[0]=='.setsym':
    	return False
    symbols[i[1].upper()],idx =expression(i[3],0)
    return True

def termc(i):
    global etc 
    if len(i)==0:
        return False
    if not i[0]=='.termc':
        return False
    p=i[3]
    s='"'
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

def readpat(fn):
    global pat
    f=open(fn,"rt")
    p=[]
    w=[]
    while(l:=f.readline()):
        l=remove_comment(l)
        l=l.replace('\n',"").replace(chr(13),'').replace('\t',' ')
        l+=chr(0)
        idx=0
        t=[]
        while l[idx]!=chr(0):
            idx=getstr_(l,idx)
            v,idx=getstr(l,idx)
            t.append(v)

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

def evalfs(s,idx):
    a=''
    while True:
        if s[idx]=='(':
            idx+=1
            v,idx=evalf(s,idx+1)
            return ("("+str(v)+")",idx)
        elif s[idx]==chr(0) or s[idx]==',' or s[idx]==';':
            break
        elif s[idx]==')':
            idx+=1
            break
        elif s[idx]==chr(0x23):
            idx+=1
            chara=s[idx]
            idx+=1
            if s[idx:idx+3]==':=(':
                chara=s[idx]
                idx+=1
                (v,idx)=evalf(s,idx+2)
                put_vars(chara,v)
                if s[idx]==')':
                    idx+=1
                else:
                    pass
            else:
                v=get_vars(chara)
            a+="("+str(v)+")"
        else:
            a+=s[idx]
            idx+=1

    return (a,idx)

def evalf(s,idx):
    x,idx=evalfs(s,idx)
    try:
        a=eval(x)
    except:
        a=-1
    else:
        pass
    return(a,idx)

def makeobj(s):
    ch=','
    s+=chr(0)
    idx=0
    cnt=0
    while True:
        (x,idx)=expression(s,idx)
        if x!=-1:
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

def getword(s,idx):
    t=""
    while not (s[idx] in etc):
        t+=s[idx].upper()
        idx+=1
    return t,idx
    
def getstr(s,idx):
    t=''
    if s[idx]=='"':
        idx+=1
    while s[idx]!='"':
        t=t+s[idx]
        idx+=1
    if s[idx]=='"':
        idx+=1
    return t,idx

def getstr_(s,idx):
    while s[idx]!=chr(0) and s[idx]!='"':
        idx+=1
    return idx

def match(s,t):
    s+=chr(0)
    t+=chr(0)
    idx_s=0
    idx_t=0
    while True:
        a=t[idx_t] # aはパターンファイル
        b=s[idx_s] # bはアセンブリライン
        if b==chr(0):
            return True
        elif a==b.upper():
            pass
        elif a==b:
            pass
        elif a in "abcdefghijklmn":
            (v,idx_s)=expression(s,idx_s)
            if idx_s==-1:
                return False
            put_vars(t[idx_t],v)
            idx_t+=1
            continue
        elif a in "opqrstuvwxyz":
            (w,idx_s)=getword(s,idx_s)
            if issymbol(w):
                put_vars(t[idx_t],symbols[w])
            idx_t+=1
            continue
        elif a!=b:
            return False
        idx_s+=1
        idx_t+=1

def error(s):
    ch=','
    s+=chr(0)
    idx=0
    error_occured=False
    while (ch:=s[idx])!=chr(0):
        if ch==',':
            idx+=1
            continue

        u,idx=evalf(s,idx)
        if s[idx]==';':
            idx+=1
        t,idx=evalf(s,idx)
        if u:
            print(f"error code {t} ")
            error_occured=True

    return error_occured

def lineassemble(line):
    line=line.replace('\t',' ')
    line=line.replace('\n','')
    line=line.upper()
    lin=[i for i in line.replace('\n','').upper().split(' ') if i]
    if not lin:
        return 0
    l=lin
    idx=0
    of=0
    prev="/*"
    se=False
    for i in pat:
        #
        # i はパターンファイルのデータ
        # l はアセンブリライン
        #
        if debug:
            print(symbols)
            print(i)
        if set_symbol(i): continue
        if termc(i): continue

        a=i[0].upper()
        if not a:
            a=prev
        else:
            prev=a
        w=[_ for _ in i if _]
        if a=='/*':
            pass
        elif a==l[0].upper():
            if len(w)==1 or len(w)==2:
                of=makeobj(i[3])
                break
            elif len(w)==3:
                if match(l[1],i[1]):
                    of=makeobj(i[3])
                    break
            elif len(w)==4:
                if match(l[1],i[1]):
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
    global pc,debug
    pc=0

    if len(sys.argv)==1:
        print("axx general assembler programmed and designed by T.Maekawa")
        print("Usage: python axx.py [-d] patternfile.axx [sourcefile.s]")
        return

    if sys.argv[1]=='-d':
        print("Debug mode")
        debug=1
        ofs=1
    else:
        ofs=0

    sys_argv=sys.argv[ofs:]
    if len(sys_argv)>=2:
        readpat(sys_argv[1])

    if len(sys_argv)==2:
        while True:
            line=input(":").replace(chr(13),'').replace('\n','')
            if line=='debug':
                debug=1
                print('debug')
                line=""
            if line=='undebug':
                debug=0
                print('undebug')
                line=""
            if debug:
                print(symbols)
            pc+=lineassemble(line)
    elif len(sys_argv)>=3:
        af=readfile(sys_argv[2])
        for i in af:
            pc+=lineassemble(i)

if __name__=='__main__':
    main()
    exit(0)
