---
title: General Assembler 'axx'
tags: Terminal assembly Python
author: fygar256
slide: false
---

# GENERAL ASSEMBLER 'axx.py'

axx.py is a generalized assembler.

It is written in a general way, so the execution platform is not dependent on a specific processing system.

It is also set to ignore chr(13) at the end of lines in DOS files. It should work on any processing system that runs python.

axx can process the instruction set of any processor if you prepare pattern data, but it does not support the practical functions of dedicated assemblers. The current version is an experimental implementation. We plan to implement the practical functions of dedicated assemblers in the future.

・How to use

Use it as follows: python axx.py 8048.axx [sample.s].

axx reads the assembler pattern data from the first argument and assembles the source file of the second argument based on the pattern data. If the second argument is omitted, the source is input from standard input.

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

mnemonic can be omitted from the second line onwards. If omitted, specify a space.

If omitted, the mnemonic from the previous line will be used.

operands may not be present. error_patterns can be omitted. binary_list cannot be omitted.

There are three types of pattern data:

```
(1) mnemonic binary_list
(2) mnemonic operands binary_list
(3) mnemonic operands error_patterns binary_list
```

・Comment

If '/*' is written in the pattern file, the part after `/*` on that line becomes a comment. Currently, you cannot close a line with `*/`. It is only valid after the `/*` on that line.

・Case sensitivity, variables

Uppercase letters in the mnemonic and operands in the pattern file are treated as character constants. Lowercase letters are treated as variables. The mnemonic and operands assign the value of the expression or symbol at that position to the variable.

Lowercase variables are referenced from error_patterns and binary_list. Lowercase letters a through n represent expressions, and lowercase letters o through z represent symbols.

The assembly line accepts uppercase and lowercase letters as the same.

The special variable in assembly line expressions is '$$', which represents the current location counter.

・Expression, value

There is an assignment operator :=. If you enter d:=24, 24 will be assigned to the variable d. The value of the assignment operator is the assigned value.

The prefix operator `#` takes the value of the symbol that follows it.

The prefix operator `@` returns the number of bits of the value that follows.

The binary operator `**` is exponentiation.

・error_patterns

error_patterns uses variables and comparison operators to specify the conditions under which an error occurs.

Multiple error patterns can be specified, separated by ','. For example, as follows:

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

, and you pass add a,rn to the assembly line, it will return error code 5 if n>7, and add a,r1 will generate binary 0x69.

・symbol

```
.setsym symbol n
```

Writing this defines symbol with the value n.

Symbols include letters, numbers, etc., but axx uses characters other than the following as constituent characters of the symbol: ,; \t\n\0()[]{}\\\"\'. This is called the termination character.

The termination character can be changed by writing the .termc command.

```
.termc ,;\t\n\0()[]{}\\
```

Here is an example of the symbol definition z80. In the pattern file,

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

The symbols B, C, D, E, H, L, A, BC, DE, HL, and SP are defined as 0, 1, 2, 3, 4, 5, 7, 0x00, 0x10, 0x20, and 0x30, respectively. Symbols are not case sensitive.

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

The C in ADD A,C will be 1, and the C in RET C will be 3.

・Example of a symbol that contains a mixture of symbols, numbers, and letters

```
.setsym $s5 21
```

・Example of binary output

```
.setsym BC 0x00
.setsym DE 0x10
.setsym HL 0x20
LD s,d (#s&0xf!=0)||(#s>>4)>3;9 s|0x01,d&0xff,d>>8
```

So `ld bc,0x1234, ld de,0x1234, ld hl,0x1234` output `0x01,0x34,0x12, 0x11,0x34,0x12, 0x21,0x34,0x12,` respectively.

・Pattern order

```
(1) LD A,(HL)
(2) LD A,d
```

Pattern files are evaluated from top to bottom, so the one placed first takes precedence.

In this case, if (1) and (2) were reversed, ld a,(hl) in the assembly line would put (hl) in the value of d, so place LD A,(HL) in the pattern file before LD A,d. Special patterns are placed first, and general patterns are placed last.

- Floating point

For example, suppose there is a processor that includes floating point operands, and MOVF fa,3.14 loads 3.14 into the fa register, with the opcode being 01. In this case, the pattern data would be

```
MOVF FA,d 0x01,d>>24,d>>16,d>>8,d
```

and if movf fa,0f3.14 is passed to the assemble line, the binary output will be 0x01,0xc3,0xf5,0x48,0x40.

- Number notation

Prefix binary numbers with '0b'.

Prefix hexadecimal numbers with '0x'.

Prefix floating point float (32bit) with '0f'.

For floating-point double (float 64bit), please prefix with '0d'.

・Error check

Error check is lax.

Version
2024/02/21 First published

2024/07/30 Sorry, there was a bug.

2024/07/30 ver 1.0.0 released

2024/08/30 Documentation update

2024/09/12 Documentation update, floating point support version 1.0.1

2024/09/12 22:30 Special variable '$' to '$$'. version 1.0.2

2024/09/13 Add eval function. version 1.0.9

2024/09/13 15:14 Expanded eval function. Fixed pattern file syntax. version 1.1.0

2024/09/13 22:00 Revised symbol definition specifications. version 1.1.5

2024/09/14 Changed pattern file description method. Evaluate errorpattern with eval function. version 1.2.0

2024/09/15 Allow symbols to be defined by symbols. version 1.2.2

2024/09/16 Reverted pattern file description method. Finally finished. version 1.3.0

2024/09/16 13:00 Add #prefix operator. version 1.3.2

2024/09/16 19:30 Added the @ prefix operator. Added the power operator. Improved the match function to correct the notation for x86_64. version 1.3.8

2024/09/17 02:40 Changed mnemonic to handle variables. version 1.4.0

2024/09/17 23:00 Added label processing. version 1.4.2

2024/09/18 Added escape character `\` to mnemonic and operand notation. version 1.4.3


MIPS example
```
.setsym $v0 2
.setsym $a0 4
ADDI x,y,d (e:=(0x20000000|(y<<21)|(x<<16)|d&0xffff))>>24,e>>16,e>>8,e
```

Assignment operator `:=` is used.

```
$ axx.py mips.axx
: addi $a0,$v0,9
0x20,0x44,0x00,0x09,
:
```


An example of x86_64 instructions

```
.setsym rax 0
.setsym rbx 3
.setsym rcx 1
LEAQ r,[s+t*d+e] 0x48,0x8d,0x04,((@d)-1)<<6|t<<3|s,e
```

```
$ axx x86_64.axx
:leaq rax,[rbx+rcx*2+0x10]
0x48,0x8d,0x04,0x4b,0x10,
```

Comments

- sorry for original notation.

- Obviously, LISP machines cannot be described.


### Thanks

I would like to express my gratitude to my mentor, Junichi Hamada, and Tokyo Denshi　Sekkei, who gave me problems and hints, the University of Electro-Communications　for their cooperation, and to some other unforgettable guys.
Thank you very much.
