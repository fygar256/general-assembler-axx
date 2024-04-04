#!/usr/bin/python3
import  sys

# simple module which evaluates expression

vars=[ 0 for i in range(26) ]

def get_vars(s):
    c=ord(s.upper())
    return vars[c-ord('A')]

def put_vars(s,v):
    global vars
    c=ord(s.upper())
    vars[c-ord('A')]=v
    return

def err(m):
    print(m)
    return -1

def factor(s,idx):
    if s[idx]=='-':
        (x,idx)=factor(s,idx+1)
        x=-x
    elif s[idx]=='~':
        (x,idx)=factor(s,idx+1)
        x=~x
    else:
        (x,idx)=factor1(s,idx)
    return (x,idx)

def factor1(s,idx):
    x = 0

    if s[idx]=='0' and (s[idx+1]=='x' or s[idx+1]=='X'):
        idx+=2
        while(s[idx].upper() in "0123456789ABCDEF"):
            x=16*x+(ord(s[idx])-0x30 if s[idx] in "0123456789" else ord(s[idx].upper())-0x41+10 )
            idx+=1

    elif s[idx] in "0123456789":
        while(s[idx] in "0123456789"):
            x=10*x+ord(s[idx])-0x30
            idx+=1
        a=1
        if (s[idx]=='.'):
            idx+=1
            while(s[idx] in "0123456789"):
                x+=(a/10)*(ord(s[idx])-0x30)
                a/=10
                idx+=1

    elif s[idx] in "abcdefghijklmnopqrstuvwxyz":
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
        if (s[idx]=='<' and s[idx+1]=='<'):
            (t,idx)=term1(s,idx+2)
            x<<=t
        elif (s[idx]=='>' and s[idx+1]=='>'):
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
        if (s[idx]=='<' and s[idx+1]=='='):
            (t,idx)=term6(s,idx+2)
            x=x<=t
        elif (s[idx]=='<'):
            (t,idx)=term6(s,idx+1)
            x=x<t
        elif (s[idx]=='>' and s[idx+1]=='='):
            (t,idx)=term6(s,idx+2)
            x=x>=t
        elif (s[idx]=='>'):
            (t,idx)=term6(s,idx+1)
            x=x>t
        elif (s[idx]=='=' and s[idx+1]=='='):
            (t,idx)=term6(s,idx+2)
            x=x==t
        elif (s[idx]=='!' and s[idx+1]=='='):
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
        if (s[idx]=='&' and s[idx+1]=='&'):
            (t,idx)=term8(s,idx+2)
            x=x and t
        else:
            break
    return (x,idx)

def term10(s,idx):
    (x,idx)=term9(s,idx)
    while True:
        if (s[idx]=='|' and s[idx+1]=='|'):
            (t,idx)=term9(s,idx+2)
            x=x or t
        else:
            break
    return (x,idx)


def expression(s,idx):
    return term10(s,idx)

def main():
    s=input("Input expression:")+chr(0)
    x,idx=expression(s,0)
    print(x)

if __name__=='__main__':
    main()
    exit(0)
