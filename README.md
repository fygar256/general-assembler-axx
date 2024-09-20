---
title: General Assembler 'axx'
tags: Terminal assembly Python
author: fygar256
slide: false
---
### GENERAL ASSEMBLER 'axx.py'

axx.py is a generalized assembler.

It is written in a general way, so it does not depend on a specific processing system.

It is also set to ignore chr(13) at the end of lines in DOS files. It should work on any processing system that runs python.

axx can process the instruction set of any processor if you prepare pattern data, but it does not support the practical functions of dedicated assemblers. The current version is an experimental implementation. We plan to implement the practical functions of dedicated assemblers in the future.

・How to use

Use it as follows: `python axx.py 8048.axx [sample.s]`.

ax reads the assembler pattern data from the first argument and assembles the source file of the second argument based on the pattern data. If the second argument is omitted, the source is input from standard input.

In axx, a line input from an assembly language source file or standard input is named an assembly line.

・Pattern data explanation

Pattern data is arranged as follows.

```
mnemonic operands error_patterns binary_list
mnemonic operands error_patterns binary_list
mnemonic operands error_patterns binary_list
:
:
```

Mnemonic can be omitted from the second line onwards. If omitted, specify a space.

If omitted, the mnemonic from the previous line will be used.

There may be no operands. Error_patterns can be omitted. Binary_list cannot be omitted.

There are three types of pattern data:

```
(1) mnemonic binary_list
(2) mnemonic operands binary_list
(3) mnemonic operands error_patterns binary_list
```

・Comments

If you write '/*' in the pattern file, the part after `/*' on that line will become a comment. Currently, you cannot close it with `*/`. It is only valid for the part after `/*` on that line.

Comments on the assembly line are `;`.

・Case sensitivity, variables

Uppercase letters in mnemonic and operands in the pattern file are treated as character constants. Lowercase letters are treated as variables. The value of the expression or symbol that corresponds to that position is assigned to the variable from mnemonic and operands.

Lowercase variables are referenced from error_patterns and binary_list. Lowercase letters a to n represent expressions, and o to z represent symbols.

The assembly line accepts uppercase and lowercase letters as the same.

A special variable in assembly line expressions is '$$', which represents the current location counter.

・Expression, value

There is an assignment operator `:=`. When `d:=24` is used, 24 is assigned to the variable d. The value of an assignment operator is the assigned value.

The prefix operator `#` takes the value of the symbol that follows.

The prefix operator `@` returns the number of bits of the value that follows. We call this the snake-like operator.

The binary operator `'`, when `a'24` is used, the 24th bit of a is made the sign bit and sign-extended. We call this the SEX operator.

The binary operator `**` is exponentiation.

The prefix operator `!` returns the value of the label that follows.

・Escape character

The escape character `\` can be used in mnemonic and operands.

・error_patterns

error_patterns uses variables and comparison operators to specify the conditions under which an error occurs.

You can specify multiple error patterns, separated by ','. For example, as follows.

```
a>3;4,b>7;5
```
In this example, if a>3, error code 4 is returned, and if b>7, error code 5 is returned.

・binary_list

binary_list specifies the codes to be output, separated by ','. For example, if you specify 0x03,#d, d will be output after 0x3.

Let's take 8048 as an example. If the pattern file contains

```
ADD A,Rn n>7;5 n|0x68
```

and you pass `add a,rn` to the assembly line, it will return error code 5 if n>7, and `add a,r1` will generate binary 0x69

・symbol

```
.setsym symbol n
```

When you write this, symbol is defined with the value n.

Symbols can be letters, numbers,

Here is an example of symbol definition z80. If you write

```
.setsym B 0
.setsym C 1
.setsym D 2
.setsym E 3
.setsym H 4
.setsym L 5
.setsym A 7
.setsym BC 0x00
.setsym DE 0x10
.setsym HL 0x20
.setsym SP 0x30
```

in a pattern file, it will define the symbols B, C, D, E, H, L, A, BC, DE, HL, and SP as 0, 1, 2, 3, 4, 5, 7, 0x00, 0x10, 0x20, and 0x30, respectively. Symbols are not case sensitive.

If there are multiple definitions of the same symbol in a pattern file, the new one will replace the old one. That is,

```
.setsym B 0
.setsym C 1
ADD A,s

.setsym NZ 0
.setsym Z 1
.setsym NC 2
.setsym C 3
RET s
```

In this case, the C in ADD A,C becomes 1, and the C in RET C becomes 3.

・Example of a symbol that contains a mixture of symbols, numbers, and letters

```
.setsym $s5 21
```

To clear all symbols, use `.clearsym`.

```
.clearsym
```

・Example of binary output

```
.setsym BC 0x00
.setsym DE 0x10
.setsym HL 0x20
LD s,d (#s&0xf!=0)||(#s>>4)>3;9 s|0x01,d&0xff,d>>8
```

Then, `ld bc,0x1234, ld de,0x1234, ld hl,0x1234` output `0x01,0x34,0x12, 0x11,0x34,0x12, 0x21,0x34,0x12`, respectively.

・Pattern order

```
(1) LD A,(HL)
(2) LD A,d
```

Pattern files are evaluated from top to bottom, so the one placed first takes precedence.

In this case, if (1) and (2) are reversed, ld a,(hl) in the assembly line will put (hl) in the value of d, so place LD A,(HL) in the pattern file before LD A,d. Place special patterns first and general patterns after.

・label

Labels can be defined from the assembly line in the following way.

```
label1:
label2: equ 0x10
label3: nop
```

To define a label with a label, do the following.

```
label4: equ !label1
```

The prefix operator `!` is used.

・ORG
ORG is

```
org 0x800
```
from the assembly line.

・Floating point

For example, suppose there is a processor that includes floating point as an operand, and `MOVF fa,3.14` loads 3.14 into the fa register, and the opcode is 01. In this case, the pattern data is

```
MOVF FA,d 0x01,d>>24,d>>16,d>>8,d
```

and if `movf fa,0f3.14` is passed to the assembly line, the binary output will be 0x01,0xc3,0xf5,0x48,0x40.

・Number notation

Prefix binary numbers with '0b'.

Prefix hexadecimal numbers with '0x'.

Please prefix floating point float (32bit) with '0f'.

Please prefix floating point double (float 64bit) with '0d'.

### MIPS example

```mips.axx
.setsym $v0 2
.setsym $a0 4
ADDI x,y,d (e:=(0x20000000|(y<<21)|(x<<16)|d&0xffff))>>24,e>>16,e>>8,e

```

Assignment operator `:=` is used.

``` $ axx.py mips.axx >> addi $a0,$v0,9 0x20,0x44,0x00,0x09, >> ```` ### Example of x86_64 instruction ````x86_64.axx .setsym rax 0 .setsym rbx 3 .setsym rcx 1 LEAQ r,[s+t*d+e] ,0x8d,0x04,((@d)-1)<<6|t<<3|s,e ``` ``` $ axx x86_64.axx >> leaq rax,[rbx+rcx*2+0x10] 0x48,0x8d,0x04,0x4b,0x10, ``` ### A64FX test

```a64fx.axx
.setsym v0 0
.setsym x0 1
ST1 {x.4\s},[y] 0x01,s,y,0
```

```
$ axx.py a64fx.axx
>> st1 {v0.4s},[x0]
0x01,0x00,0x01,0x00,
>>
```

-Error check

Error check is weak.

### Comment

-Please forgive the variation in notation.

-I think it will work on a scalar processor. I don't think there are any processors that directly store matrices and vectors in registers.

### Future work

-Make it possible to write spaces in operands.

### Acknowledgements

I would like to express my gratitude to my mentor, Junichi Hamada, and Tokyo Denshi Sekkei, who gave me the problems and hints, to the University of Electro-Communications, who cooperated with me, and to some other unforgettable guys. Thank you very much.
