---
title: General Assembler 'axx'
tags: Terminal Python general assembler
author: fygar256
slide: false
---
GENERAL ASSEMBLER 'axx.py'

axx.py is a general assembler that generalizes assemblers.

The execution platform is not dependent on a specific processing system. It is also set to ignore chr(13) at the end of lines in DOS files. I think it will work on any processing system that runs python.

axx can process the instruction set of any processor if you prepare pattern data, but it does not support the practical functions of a dedicated assembler. The current version is a trial implementation. I also intend to implement the practical functions of a dedicated assembler in the future.

Also, because the pattern files are separate from the source files, it is possible to generate machine code for a processor with one instruction set from a source file with a different instruction set, provided that coding effort is not taken into consideration.


#### How to use

Use it like this: `python axx.py patternfile.axx [[sample.s] outfile.bin]`.

axx reads assembler pattern data from the first argument and assembles the source file of the second argument based on the pattern data. If the second argument is omitted, the source is input from standard input.

The result is output as text to standard output, and at the same time a binary file named `axx.out` is output to the current directory.

In axx, assembly language source files and lines input from standard input are named assembly lines.

#### Explanation of pattern data

Pattern data is arranged as follows.

```
mnemonic operands error_patterns binary_list
mnemonic operands error_patterns binary_list
mnemonic operands error_patterns binary_list
:
:
```

Mnemonic can be omitted from the second line onwards. If omitted, specify a space. If omitted, the mnemonic from the previous line will be used.

operands may not be present. error_patterns can be omitted. binary_list cannot be omitted.

There are three types of pattern data:

```
(1) mnemonic binary_list
(2) mnemonic operands binary_list
(3) mnemonic operands error_patterns binary_list
```

#### Comments

Writing `/*` in a pattern file makes the part after `/*` on that line a comment. Currently, you cannot close it with `*/`. It is only valid for the part after `/*` on that line.

Assembly line comments are `;`.

#### Case sensitivity, variables

Uppercase letters in mnemonic and operands in the pattern file are treated as character constants. Lowercase letters are treated as one-character variables. The values ​​of factors, expressions, and symbols that correspond to that position in mnemonic and operands are assigned to variables from the assembly line and are referenced from error_patterns and binary_list.

Lowercase letters a through g represent expressions, h through n represent constants or other factors, and o through z represent symbols. All unassigned variables have an initial value of 0.

The assembly line accepts uppercase and lowercase letters as the same.

A special variable is '$$', which represents the current location counter.

#### Operator precedence

The operators and precedence are as follows, based on Python

```
(expression)      An expression enclosed in parentheses
#                 An operator that returns the value of a symbol
-,~               Negative, bitwise NOT
@                 A unary operator that returns the bit position from the right of the most significant bit of the following value
:=                Assignment operator
**                Exponentiation
*,//              Multiplication, integer division
+,-               Addition, subtraction
<<,>>             Left shift, right shift
&                 Bitwise AND
|                 Bitwise OR
'                 Sign extension
<=,<,>,>=,!=,==   Comparison operators
not(x)            Logical NOT
&&                Logical AND
||                Logical OR
```

There is an assignment operator `:=`. If you enter `d:=24`, 24 will be assigned to the variable d. The value of the assignment operator is the assigned value.

The prefix operator `#` takes the value of the symbol that follows it.

The prefix operator `@` returns the number of bits in the value that follows. We call this the snake-shaped Marmatta operator.

The binary operator `'`, for example `a'24`, will sign extend (Sign EXtend) the 24th bit of a as the sign bit. We call this the SEX operator.

The binary operator `**` is exponentiation.

#### Escape character

You can use the escape character `\` in mnemonic and operands.

#### error_patterns

error_patterns uses variables and comparison operators to specify the conditions under which an error occurs.

Multiple error patterns can be specified, separated by ','. For example, as follows.

```
a>3;4,b>7;5
```
In this example, if a>3, error code 4 is returned, and if b>7, error code 5 is returned.

#### binary_list

binary_list specifies the code to be output, separated by ','. For example, if you specify 0x03,d, d will be output after 0x3.

Let's take 8048 as an example. If the pattern file contains

```
ADD A,Rn n>7;5 n|0x68
```

and you pass `add a,rn` to the assembly line, it will return error code 5 when n>7, and `add a,r1` will generate binary 0x69.

#### symbol

```
.setsym symbol n
```

When you write this, symbol is defined with value n.

Symbols are letters, numbers, and strings of several symbols.

To define symbol2 with symbol1, write as follows.

```
.setsym symbol1 1
.setsym symbol2 #symbol1
```

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

#### Example of binary output

```
.setsym BC 0x00
.setsym DE 0x10
.setsym HL 0x20
LD s,d (s&0xf!=0)||(s>>4)>3;9 s|0x01,d&0xff,d>>8
```

Then, `ld bc,0x1234, ld de,0x1234, ld hl,0x1234` output `0x01,0x34,0x12, 0x11,0x34,0x12, 0x21,0x34,0x12`, respectively.

#### Pattern order

```
(1) LD A,(HL)
(2) LD A,d
```

Pattern files are evaluated from top to bottom, so the one placed first takes precedence. Special patterns are placed first, and general patterns are placed last.

#### Double brackets

Optional mnemonic and operands can be enclosed in double brackets. This shows the `inc (ix)` command of the z80.

```
INC (IX[[+d]]) 0xdd,0x34,d
```

In this case, the initial value of the lowercase variable is 0, so `inc (ix+0x12)` is output as `0xdd,0x34,0x12` if not omitted, and `inc (ix)` is output as `0xdd,0x34,0x00` if omitted.

#### label

Labels can be defined from the assembly line in the following way.

```
label1:
label2: .equ 0x10
label3: nop
```

A label is a string of letters, numbers, and symbols, starting with a non-numeric ``.`, alphabet, or symbol, and is two or more characters long.

To define a label with a label, do the following:

```
label4: .equ label1
```

#### ORG

ORG is set to

```
.org 0x800
```
from the assemble line.

#### alignment and padding

Setting

```
.padding 0x12
```

from the pattern file will set the padding bytecode to 0x12. The default is 0x00.

Setting

```
.align 16
```

from the assemble line will align to 16.

#### Quotation

If you want to write a space in the pattern file, enclose it in double quotation marks`"`.

```
ADD "A , Rn" "n > 7 ; 5" "n | 0x68"
```

is the same as

```
ADD A,Rn n>7;5 n|0x68
```

.
#### Floating point, number notation

For example, suppose there is a processor that includes floating point operands, and `MOVF fa,3.14` loads 3.14 into the fa register, and the opcode is 01. In that case, the pattern data is

```
MOVF FA,d 0x01,d>>24,d>>16,d>>8,d
```

Then, the assemble line is `movf fa,0f3.14`, the binary output will be 0x01,0xc3,0xf5,0x48,0x40.

Prefix binary numbers with '0b'.

Prefix hexadecimal numbers with '0x'.

Prefix floating point floats (32bit) with '0f'.

Prefix floating point doubles (float 64bit) with '0d'.

### Tests of some instructions on some processors

This is a test, so the binary will not be the actual code.

```test.axx
/* ARM64
.setsym r1 2
.setsym r2 3
.setsym r3 4
.setsym lsl 6
ADD "w, x, y z #d" 0x88,d

/* A64FX
.setsym v0 0 
.setsym x0 1 
ST1 {x.4S},[y] 0x01,x,y,0 

/* MIPS 
.setsym $s5 21 
.setsym $v0 2 
.setsym $a0 4 
ADDI x,y,d (e:=(0x20000000|(y<<21)|(x<<16)|d&0xffff))>>24,e> >16,e>>8,e

/* x86_64 
.setsym rax 0 
.setsym rbx 3 
.setsym rcx 1 
LEAQ r,[s,t,d,e] 0x48,0x8d,0x04,((@d)-1)<<6|t<<3|s,e 
LEAQ "r,[ s + t * h + i ]" 0x48,0x8d,0x04,((@h)-1)<<6|t<<3|s,i 
```

```test.s
leaq rax , [ rbx , rcx , 2 , 0x40]
leaq rax , [ rbx + rcx * 2 + 0x40]
addi $v0,$a0,5
st1 {v0.4s},[x0]
add r1, r2, r3 lsl #20
```

Example 

```
$ axx.py test.axx test.s
0x48,0x8d,0x04,0x4b,0x40,
0x48,0x8d,0x04,0x4b,0x40,
0x20,0x82,0x00,0x05,
0x01,0x00,0x01,0x00,
0x88,0x14,
```

### Comments

・Sorry for original notation.

・Error checking is lax.

・I know this is a bit ridiculous, but quantum computers and LISP machines are not supported.

・From homemade processors to supercomputers, you can use it.

・Runtime variable-length byte instructions are not supported.

## Future issues

・The order of evaluation of pattern files is difficult, so we will do something about it.

・As it stands now, it can only assemble a single file, so we will make it possible to handle the linker.

・Improve the handling of symbols, labels, and variables.

・Add practical functions

・Perform more error checking.

・Allow multiple omission double brackets. To do this, enclose the expression in `{{',`}}` so that it will accept multiple operands.

- Escape characters in expressions do not work, and I would like to solve this problem.

- x86_64 MMX and AVX instructions require the alignment to be specified in advance, and I would like to solve this problem.

・It's no good because it's divided into two parts, mnemonic and operands. I want to unify it into one, mnemonic+operands=instruction. However, for traditional reasons, it's currently divided into two.

### Acknowledgements
I would like to express my gratitude to my mentor, Junichi Hamada, and Tokyo Denshi Sekkei, who gave me the problems and hints, to the University of Electro-Communications, who cooperated with me, IEEE, Qiita, and to some other unforgettable guys. Thank you very much.
