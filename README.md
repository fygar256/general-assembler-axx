---
title: General Assembler 'axx'
tags: Terminal assembly Python
author: fygar256
slide: false
---

# GENERAL ASSEMBLER 'axx.py'

axx.py is a generalized assembler.

The execution platform is not dependent on a specific processing system. It is also set to ignore chr(13) at the end of lines in DOS files. It should work on any processing system that runs python.

axx can process the instruction set of any processor if you prepare pattern data, but it does not support the practical functions of dedicated assemblers. The current version is an experimental implementation. We plan to implement the practical functions of dedicated assemblers in the future.

・How to use

Use it as follows: `python axx.py 8048.axx [sample.s]`.

axx reads the assembler pattern data from the first argument and assembles the source file of the second argument based on the pattern data. If the second argument is omitted, the source is input from standard input.

The results are output as text to standard output, and at the same time a binary file named `axx.out` is output to the current directory.

In axx, the assembly language source file or the lines input from standard input are called assembly lines.

・Explanation of pattern data

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

If you write `/*` in the pattern file, the part after `/*` on that line will become a comment. Currently, you cannot close it with `*/`. It is only valid for the part after `/*` on that line.

Comments on the assembly line are `;`.

・Case sensitivity, variables

Uppercase letters in mnemonic and operands in the pattern file are treated as character constants. If they are lowercase, they are treated as one-character variables. From mnemonic and operands, the value of the expression or symbol that corresponds to that position is assigned to the variable.

Lowercase variables are referenced from error_patterns and binary_list. Lowercase letters a to n represent expressions, and o to z represent symbols.

From the assembly line, uppercase and lowercase are accepted as the same.

The special variable in assembly line expressions is '$$', which represents the current location counter.

### Operator precedence

The operators and precedence are based on Python and are as follows

```
(expression) An expression enclosed in parentheses
!,# Operators that return the value of a label, operators that return the value of a symbol
-,~ Negative, bitwise NOT
@ Unary operator that returns the number of bits in the value that follows
:= Assignment operator
** Power
*,// Multiplication, integer division
+,- Addition, subtraction
<<,>> Left shift, right shift
& Bitwise AND
| Bitwise OR
' Sign extension
<=,<,>,>=,!=,== Comparison operators
not(x) Logical NOT
&& Logical AND
|| Logical OR
```

There is an assignment operator `:=`. If you enter `d:=24`, 24 will be assigned to the variable d. The value of an assignment operator is the assigned value.

The prefix operator `#` takes the value of the symbol that follows.

The prefix operator `@` returns the number of bits in the value that follows. We call this the snake-shaped operator.

The binary operator `'`, for example `a'24`, sign extends the 24th bit of a as the sign bit (sign EXtend). We call this the SEX operator.

The binary operator `**` is exponentiation.

The prefix operator `!` returns the value of the label that follows. Even without a prefix operator, label returns the value of label.

・Escape character

You can use the escape character `\` in mnemonic and operands.

・error_patterns

error_patterns uses variables and comparison operators to specify the conditions that will cause an error.

Multiple error patterns can be specified, separated by ','. For example, as follows.

```
a>3;4,b>7;5
```
In this example, when a>3, it returns error code 4, and when b>7, it returns error code 5.

・binary_list

binary_list specifies the code to be output, separated by ','. For example, if you specify 0x03,d, d will be output after 0x3.

Let's take 8048 as an example. If the pattern file contains

```
ADD A,Rn n>7;5 n|0x68
```

and you pass `add a,rn` to the assembly line, it will return error code 5 when n>7, and `add a,r1` will generate binary 0x69.

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
LD s,d (s&0xf!=0)||(s>>4)>3;9 s|0x01,d&0xff,d>>8
```

Then, `ld bc,0x1234, ld de,0x1234, ld hl,0x1234` output `0x01,0x34,0x12, 0x11,0x34,0x12, 0x21,0x34,0x12`, respectively.

・Pattern order

```
(1) LD A,(HL)
(2) LD A,d
```

Pattern files are evaluated from top to bottom, so the first one takes precedence.

In this case, if (1) and (2) are reversed, ld a,(hl) in the assembly line will result in (hl) being entered as the value of d, so place LD A,(HL) in the pattern file before LD A,d. Place special patterns first and general patterns after.

・label

Labels can be defined from the assembly line in the following way.

```
label1:
label2: equ 0x10
label3: nop
```

Labels are strings of letters, numbers, and symbols that begin with a non-numeric character and are two or more characters long.

To define a label with a label, do the following.

```
label4: equ label1
```

・ORG

ORG is defined from the assembly line as

```
org 0x800
```

・Quotes

If you want to write spaces in the pattern file, enclose it in double quotes`"`.

```
ADD A,Rn "n > 7 ; 5" "n | 0x68"
```

is the same as

```
ADD A,Rn n>7;5 n|0x68
```

.
・Floating point

For example, suppose there is a processor that includes floating point operands, and `MOVF fa,3.14` loads 3.14 into the fa register, and the opcode is 01. In this case, the pattern data is

```
MOVF FA,d 0x01,d>>24,d>>16,d>>8,d
```

The assembly line will contain `movf If you pass fa,0f3.14, the binary output will be 0x01,0xc3,0xf5,0x48,0x40.

-Number notation

Prefix binary numbers with '0b'.

Prefix hexadecimal numbers with '0x'.

Prefix floating-point numbers (32bit) with '0f'.

Prefix floating-point numbers (64bit) with '0d'.

### MIPS example

```mips.axx
.setsym $v0 2
.setsym $a0 4
ADDI x,y,d (e:=(0x20000000|(y<<21)|(x<<16)|d&0xffff))>>24,e>>16,e>>8,e

```

Assignment operator `:=` is used.

```
$ axx.py mips.axx
>> addi $a0,$v0,9
0x20,0x44,0x00,0x09,
>>
```

### Example of x86_64 command

```x86_64.axx
.setsym rax 0
.setsym rbx 3
.setsym rcx 1
LEAQ r,[s,t,d,e] 0x48,0x8d,0x04,((@d)-1)<<6|t<<3|s,e
```

``` 
$ axx x86_64.axx
>> leaq rax,[rbx,rcx,2,0x10] 0x48,0x8d,0x04,0x4b,0x10,
```

### Testing A64FX 

````a64fx.axx 
.setsym v0 0
.setsym x0 1
ST1 {x.4\s},[y] 0x01,x,y,0
```

```
$ axx.py a64fx.axx
>> st1 {v0.4s},[x0]
0x01,0x00,0x01,0x00,
>>
```

-Error checking

Error checking is insufficient.

### Comments

-Please excuse the inconsistencies in notation.

-I think it can handle memory vector machines, but it probably can't handle vector register machines due to the notation.

### Future issues

-The order of evaluation of pattern files is difficult, so I'll do something about it.

-As it stands now, it can only assemble a single file, so I'll make it so that the linker can handle it.

### Acknowledgements

I would like to express my gratitude to my mentor, Junichi Hamada, and Tokyo Electronics Design for giving me problems and hints, the University of Electro-Communications for their cooperation, and to some other unforgettable guys. Thank you very much.
