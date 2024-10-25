#!/usr/bin/python
import sys
import axx
pas=0
current_section=".default"
sections={ '.default' :['']}

def skipspc(s,idx):
    while len(s)>idx:
        if s[idx]==' ':
            idx+=1
            continue
        break
    return idx


def get_label_word(s,idx):
    idx=skipspc(s,idx)
    t=""
    if len(s)>idx and (s[idx]=='.' or s[idx] in axx.lwordchars):
        t=s[idx]
        idx+=1
        while len(s)>idx:
            if not s[idx] in axx.lwordchars : 
                break
            t+=s[idx]
            idx+=1
    return t,idx

def readsections(infile):
    global sections,current_section
    with open(infile,"rt") as inf:
        while True:
            l=inf.readline().replace(chr(13),'')
            if l=='':
                return True
            l=l.replace('\n','')

            (sec,idx)=get_label_word(l,0)
            if sec.upper()==".SECTION":
                (secname,idx)=get_label_word(l,idx)
                if secname==current_section:
                    continue
                else:
                    current_section=secname
                    continue
            else:
                if current_section in sections:
                    sections[current_section]=sections[current_section]+[l]
                else:
                    sections[current_section]=[l]

def writesections(fn):
    with open(fn,"wt") as outfile:
        l=list(sections.items())
        print(l)
        for i in l:
            (a,b)=i
            outfile.write(".section    ")
            outfile.write(a)
            outfile.write('\n')
            for k in b:
                outfile.write(k)
                outfile.write('\n')

if __name__=='__main__':
    readsections(sys.argv[1])
    print(sections)
    writesections(sys.argv[2])
