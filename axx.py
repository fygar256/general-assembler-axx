#!/usr/bin/python3
import sys
import expression
pc=0
capital="ABCDEFGHIJKLMNOPQRSTUVWXYZ"
lower="abcdefghijklmnopqrstuvwxyz"
alphabet=lower+capital
symbols={}

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
    
def set_symbol(l):
    if not (len(l)>=1 and l[0]=='$'):
    	return
    idx=1
    l+=chr(0)
    (w,idx)=getword(l,1)
    if l[idx]=='=':
        idx+=1
        (v,idx)=expression.expression(l,idx)
        symbols[w.upper()]=v

def remove_comment(l):
    idx=0
    while idx<len(l):
        if len(l[idx:])>2 and l[idx]=='/' and l[idx+1]=='/':
            if idx==0:
                return ""
            else:
                return l[0:idx-1]
        idx+=1
    return l

def readpat(fn):
    f=open(fn,"rt")
    p=[]
    while(l:=f.readline()):
        head=l[0]
        l=remove_comment(l)
        l=l.replace('\n','')
        s=l.split(' ')
        t=[ i for i in s if i]
        if head==' ':
            t=['']+t
        if len(t)==1:
            t=[t[0],'','','']
        elif len(t)==2:
            t=[t[0],'','',t[1]]
        elif len(t)==3:
            t=[t[0],t[1],'',t[2]]
        elif len(t)==4:
            pass
        p.append(t)
    f.close()
    return [i for i in p if i]

def hexp(n):
    hexdigits="0123456789abcdef"
    return "0x"+hexdigits[(n&0xf0)//16]+hexdigits[n%16]

def makeobj(s):
    global pc
    ch=','
    s+=chr(0)
    idx=0
    cnt=0
    while ch!=chr(0):
        (x,idx)=expression.expression(s,idx)
        print(f"{hexp(x)},",end='')
        cnt+=1
        ch=s[idx]
        if ch==',':
            idx+=1
    print("")
    return cnt

def getword(s,idx):
    t=""
    while s[idx].upper() in capital:
        t+=s[idx].upper()
        idx+=1
    return t,idx
    
def match(s,t):
    s+=chr(0)
    t+=chr(0)
    idx_s=0
    idx_t=0
    while True:
        a=t[idx_t]
        b=s[idx_s]
        if a==chr(0) and b==chr(0):
            return True
        if a in capital and a==b.upper():
            pass
        elif a==b:
            pass
        elif a in "abcdefghijklmn":
            (v,idx_s)=expression.factor(s,idx_s)
            if idx_s==-1:
                return False
            expression.put_vars(t[idx_t],v)
            idx_t+=1
            continue
        elif a in "opqrstuvwxyz":
            (w,idx_s)=getword(s,idx_s)
            if issymbol(w):
                expression.put_vars(t[idx_t],symbols[w])
            idx_t+=1
            continue
        elif a!=b:
            return False
        idx_s+=1
        idx_t+=1

def errorchk(s):
    idx=0
    s+=chr(0)
    ef=False
    while True:
        (x,idx)=expression.expression(s,idx)
        if s[idx]==';':
            idx+=1
            (e,idx)=expression.expression(s,idx)
        if x:
            ef=True
            print(f"error code:{e}")
            if s[idx]==',':
                idx+=1
                continue
            break
        break
    return ef

def lineassemble(pat,line):
    if line=="" or line=="\n":
        return 0
    expression.put_vars('z',pc)
    prev=''
    l=[i for i in line.replace('\n','').upper().split(' ') if i]
    idx=0
    of=0
    for i in pat:
        set_symbol(i[0])
        a=i[0]
        if a=='':
            a=prev
        prev=a
        if len(l)==0:
            continue
        if a==l[0]:
            if len(l)==1:
                of=makeobj(i[3])
                break
            elif len(l)==2 and match(l[1],i[1]):
                if not errorchk(i[2]):
                    of=makeobj(i[3])
                    break
    if not of:
        print("Mnemonic error.")
    return of

def main():
    global pc
    pc=0

    if len(sys.argv)==1:
        print("Usage: axx.py patternfile.axx [sourcefile.asm]")
        return

    if len(sys.argv)>=2:
        pat=readpat(sys.argv[1])
    if len(sys.argv)==2:
        while line:=input(":"):
            pc+=lineassemble(pat,line)
    elif len(sys.argv)==3:
        af=readfile(sys.argv[2])
        for i in af:
            pc+=lineassemble(pat,i)

if __name__=='__main__':
    main()
    exit(0)
