---
title: Generalized assembler 'axx General Assembler'
tags: Terminal Python general assembler
author: fygar256
slide: false
---
GENERAL ASSEMBLER 'axx.py'

It was written in python, so the nickname is Paxx.

# Test environment

Arch linux terminal

# Main text

axx.py is a generalized assembler. It can process any processor architecture. To process each processor architecture, a pattern file (processor description file) is required. You can define any instruction, but if you create a pattern file based on the assembly language of the target processor, you can process the assembly language of that processor, although the notation is slightly different.

The execution platform is also independent of a specific processing system. It is also set to ignore chr(13) at the end of lines in DOS files. I think it will work on any processing system that runs python.

This version only includes the core of the assembler, so it does not support practical features such as optimization, advanced macros, and debuggers that are available in dedicated assemblers. For practical features, please use a preprocessor for macros. For now, please use a program that manages binary files and label (symbol) files as a linker/loader. Since this is not an IDE, please use an external debugger as a debugger. Optimization is not supported.

Since the pattern file and source file are separated, it is possible to generate machine code for another processor from source of a certain instruction set, if you do not mind the effort of coding. It is also possible to generate machine code for different processors from a common language. If you write multiple instruction codes in the binary_list of pattern data, it functions as a macro, but it is not very smart. This allows you to write a simple compiler.

Pattern data does not have control syntax other than assignment. It can be used to generate binaries, not limited to assembly language.

Since assembly language has a one-to-one correspondence with processor instructions, axx was realized.

axx reads assembler pattern data from the first argument and assembles the source file of the second argument based on the pattern data. If the second argument is omitted, the source is input from the terminal (standard input).

The result is output as text to standard output, and if there is an argument specified with the `-o` option, a binary file is output to the current directory. The `-e` option outputs the labels specified with `.export` along with section/segment information to a file in TSV format.

In axx, the lines input from an assembly language source file or standard input are named assembly lines.

## install and execution(assemble)

```
# install
git clone https://github.com/fygar256/general-assembler-axx.git
cd general-assembler-axx
chmod +x axx.py
sudo mv axx.py /usr/bin/axx

# execution(assemble)
axx patternfile.axx [source.s] [-o outfile.bin] [-e expfile.tsv] [-i impfile.tsv]
```

## Explanation of pattern files

Pattern files are processor description files that can define any instruction set. They are user-defined to correspond to individual processors. They are a kind of meta-language for machine code and assembly language.

The pattern data in a pattern file is arranged as follows:

```
instruction :: error_patterns :: binary_list
instruction :: error_patterns :: binary_list
instruction :: error_patterns :: binary_list
:
:
```

instruction cannot be omitted. error_patterns can be omitted. binary_list cannot be omitted.

instruction, error_patterns, and binary_list should be separated by `::`.

for ex. (x86_64)

```
RET :: 0xc3
```

#### Comments

If you write `/*` in a pattern file, the part after `/*` on that line becomes a comment. Currently, you cannot close it with `*/`. It is only valid for the part after `/*` on that line.

#### Case sensitivity, variables

Uppercase letters in the instruction in the pattern file are treated as character constants. If you use lowercase letters, it will be treated as a one-character variable. The value of the symbol at that position from the assembly line will be assigned to the variable. If you use `! lowercase letters`, the value of the expression at that position will be assigned, and if you use `!! lowercase letters`, the value of the factor at that position will be assigned, and they will be referenced from error_patterns and binary_list. All variables that are not assigned will have an initial value of 0. When referencing from error_patterns and binary_list, `!` is not necessary. All values ​​will be referenced in the same way.

From the assembly line, uppercase and lowercase letters are accepted as the same, except for labels and section names.

The special variable is '$$', which represents the current location counter.

#### Escape character

You can use the escape character `\` in instruction.

#### error_patterns

error_patterns uses variables and comparison operators to specify the conditions under which an error will occur.

Multiple error patterns can be specified, separated by ','. For example, as follows.

```
a>3;4,b>7;5
```
In this example, when a>3, it returns error code 4, and when b>7, it returns error code 5.

#### binary_list

binary_list specifies the code to be output, separated by ','. For example, if you specify 0x03,d, d will be output after 0x3.

Let's take 8048 as an example. If the pattern file contains

```
ADD A,R!n :: n>7;5 :: n|0x68
```

and you pass `add a,rn` to the assembly line, when n>7, it returns error code 5 (Register out of range), and when `add a,r1` is used, it generates the binary 0x69.

If the element of binary_list is empty, it will be aligned. If you start with `,` or `0x12,,0x13`, the empty part will be padded up to the exact address.

If an element of binary_list starts with `;`, if that element is 0, it will not be output.

#### symbol

```
.setsym :: symbol :: n
```

Writing this defines symbol with value n.

Symbols are letters, numbers, and strings of several symbols.

To define symbol2 with symbol1, write as follows.

```
.setsym ::symbol1 ::1
.setsym ::symbol2 ::#symbol1
```

Here is an example of symbol definition for z80. If you write the following in a pattern file:

```
.setsym ::B ::0
.setsym ::C ::1
.setsym ::D ::2
.setsym ::E ::3
.setsym ::H ::4
.setsym ::L ::5
.setsym ::A ::7
.setsym ::BC ::0x00
.setsym ::DE ::0x10
.setsym ::HL ::0x20
.setsym ::SP ::0x30
```

The symbols B, C, D, E, H, L, A, BC, DE, HL, and SP will be defined as 0, 1, 2, 3, 4, 5, 7, 0x00, 0x10, 0x20, and 0x30, respectively. Symbols are not case sensitive.

If there are multiple definitions of the same symbol in a pattern file, the new one will replace the old one. That is,

```
.setsym ::B::0
.setsym ::C::1
ADD A,s

.setsym ::NZ::0
.setsym ::Z::1
.setsym ::NC::2
.setsym ::C ::3
RET s
```
In this case, the C in ADD A,C is 1, and the C in RET C is 3.

・Example of a symbol that contains a mixture of symbols, numbers, and letters

```
.setsym ::$s5:: 21
```

To clear a symbol, use `.clearsym`.

```
.clearsym::ax
```

The above example undefines the symbol `ax`.

To clear everything, do not specify any arguments.

```
.clearsym
```

You can determine the character set to use for symbols from within the pattern file.

```
.symbolc::<characters>
```

You can specify characters other than numbers and uppercase and lowercase letters in `<characters>`.

The default is alphabets + numbers + `'_%$-~&|'`.

#### Pattern order

Pattern files are evaluated from top to bottom, so the one placed earlier takes precedence. Place special patterns first and general patterns last. Like below.

```
LD A,(HL)
LD A,e
```

#### Double brackets

Optional items in the instruction can be enclosed in double brackets. Here is the z80 `inc (ix)` instruction.

```
INC (IX[[+!d]]) :: 0xdd,0x34,d
```

In this case, the initial value of the lowercase variable is 0, so if you specify `inc (ix+0x12)`, `0xdd,0x34,0x12` will be output if you do not omit it, and if you specify `inc (ix)`, `0xdd,0x34,0x00` will be output if you omit it.

#### Specifying the padding bytecode

If you specify 

```
.padding 0x12
```

from the pattern file, the padding bytecode will be 0x12. The default is 0x00.

#### include

This will allow you to include a file.

```
.include "file.axx"
```

## Assembly file description

#### label

From the assembly line, labels can be defined in the following way.

```
label1:
label2: .equ 0x10
label3: nop
```

A label is a string of letters, numbers, and some symbols that starts with a non-numeric `.`, alphabet, or some symbol.

To define a label with a label, do the following:

```
label4: .equ label1
```

You can determine the character set to use for labels from within the pattern file.

```
.labelc::<characters>
```

You can specify characters other than numbers and uppercase and lowercase alphabets with `<characters>`.

The default is alphabet + numbers + underscore + period.

If you add `:` after the label reference, it will check for undefined label errors. In assembly languages ​​that use `:`, put a space after the label reference.

#### ORG

ORG is specified as follows:

```
.org 0x800
or
.org 0x800,p
```

From the assembly line. .org changes the location counter value. If `,p` is specified, and the previous location counter value is smaller than the value specified by .org, it will be padded to the value specified by .org.

#### Alignment

If you specify:

```
.align 16
```

From the assembly line, it will be aligned to 16 (padded with the bytecode specified by .padding up to an address that is a multiple of 16). If the argument is omitted, it will be aligned to the number specified by the previous .align or the default value.

#### Floating point, number notation

For example, suppose you have a processor that includes floating point operands, and `MOVF fa,3.14` loads 3.14 into the fa register, with the opcode being 01. In this case, the pattern data is

```
MOVF FA,!d ::0x01,d>>24,d>>16,d>>8,d
```

If you pass `movf fa,0f3.14` to the assemble line, the binary output will be 0x01,0xc3,0xf5,0x48,0x40.

Prefix binary numbers with '0b'.

Prefix hexadecimal numbers with '0x'.

Prefix floating point float (32bit) with '0f'.

For floating-point double (float 64bit), prefix with '0d'.

#### string

`.ascii` outputs the bytecode of a string, and `.asciiz` outputs the bytecode of a string with 0x00 at the end.

```
.ascii "sample1"
.asciiz "sample2"
```

#### export

As shown below, you can export the label along with the section/segment information. Only the label specified by the .export command will be exported.

```
.export label
```

#### section

As shown below, you can specify the section/segment.

```
section .text
or
segment .text
```

Currently, section and segment have the same meaning.

#### section sort

For example,

```
section .text
ld a,9
section .data
.asciiz "test1"
section .text
ld b,9
section .data
db 0x12
```

If you do this, the data will be arranged exactly as it is, so use section sort to sort it.

https://qiita.com/fygar256/items/fd590cab2078a4e8b866

```
section .text
ld a,9
ld b,9
section .data
.asciiz "test1"
db 0x12
```

#### Comments

Assembly line comments are `;`.

## Expressions, operators

Assembly line expressions and pattern data expressions call the same functions, so they work almost the same. Lowercase variables cannot be referenced from the assembly line.

#### Operator precedence

The operators and precedence are as follows, based on Python

```
(expression)       An expression enclosed in parentheses
#                  An operator that returns the value of a symbol
-,~                Negative, bitwise NOT
@                  A unary operator that returns the bit position from the right of the most significant bit of the following value
:=                 Assignment operator
**                 Exponentiation
*,//               Multiplication, integer division
+,-                Addition, subtraction
<<,>>              Left shift, right shift
&                  Bitwise AND
|                  Bitwise OR
^                  Bitwise XOR
'                  Sign extension
<=,<,>,>=,!=,==    Comparison operators
not(x)             Logical NOT
&&                 Logical AND
||                 Logical OR
```

There is an assignment operator `:=`. If you enter `d:=24`, 24 will be assigned to the variable d. The value of the assignment operator is the assigned value.

The prefix operator `#` takes the value of the following symbol.

The prefix operator `@` returns the position of the most significant bit of the value that follows from the right. We call this the Hebimarumatta operator.

The binary operator `'`, for example `a'24`, sign extends (Sign EXtends) the 24th bit of a as the sign bit. We call this the SEX operator.

The binary operator `**` is exponentiation.


## Example of binary output

```
.setsym:: BC:: 0x00
.setsym:: DE:: 0x10
.setsym:: HL:: 0x20
LD s,!d:: (s&0xf!=0)||(s>>4)>3;9 :: s|0x01,d&0xff,d>>8
```

Then, `ld bc,0x1234, ld de,0x1234, ld hl,0x1234` output `0x01,0x34,0x12, 0x11,0x34,0x12, 0x21,0x34,0x12`, respectively.

### Testing some instructions on some processors

Because this is a test, the binary is different from the actual code.

```test.axx
/* test
.setsym ::a:: 7
.setsym ::b:: 1
.setsym ::%% ::7
.setsym ::||:: 8
LD s,x :: 0x1,y,s,x

/* ARM64
.setsym ::r1 :: 2
.setsym ::r2 :: 3
.setsym ::r3 :: 4
.setsym ::lsl:: 6
ADD w, x, y z #!d :: 0x88,d
ADD x, y, !e :: 0x91,x,y,e

/* A64FX
.setsym ::v0 :: 0
.setsym ::x0 :: 1
ST1 {x.4S},[y] :: 0x01,x,y,0

/* MIPS
.setsym ::$s5 ::21
.setsym ::$v0 ::2
.setsym ::$a0 ::4
ADDI x,y,!d :: (e:=(0x20000000|(y<<21)|(x<<16)|d&0xffff))>>24,e>>16,e>>8,e

/ * x86_64
.setsym ::rax:: 0
.setsym ::rbx:: 3
.setsym ::rcx ::1
.setsym ::rep ::0xf3

MMX A,B :: ,0x12,0x13
LEAQ r,[s,t,!d,!e] :: 0x48,0x8d,0x04,((@d)-1)<<6|t<<3|s,e
LEAQ r, [ s + t * !!h + !!i ] :: 0x48,0x8d,0x04,((@h)-1)<<6|t<<3|s,i
[[z]] MOVSB ​​:: ;z,0xa4
TEST :: 0x12,,0x13

/* ookakko test
LD (IX[[+!d]]),(IX[[+!e]]):: 0xfd,0x04,d,e
NOP :: 0x01
```

The notation `LEAQ r,[s+t*h+i]` in x86_64 is `LEAQ r,[s+t*!!h+!!i]`. If you write `!h` instead of `!!h`, the evaluation function for the formula will interpret the part after 2 in `leaq rax,[rbx+rcx*2+0x40]` as `!h`, and the part beyond that, 2+0x40, as a formula, and 2+0x40 will be substituted for h, leaving the remaining `+!!i`, resulting in a syntax analysis error. This is because `!!h` represents a factor, and `!h` represents an formula. This is also because escape characters in formulas cannot be processed.

```test.s 
leaq rax , [ rbx , rcx , 2 , 0x40]
leaq rax , [ rbx + rcx * 2 + 0x40]
movsb
rep movsb
addi $v0,$a0,5
st1 {v0.4s},[x0]
add r1, r2, r3 lsl #20
```

Example 

```
$ axx.py test .axx test.s
0000000000000000: leaq rax , [ rbx , rcx , 2 , 0x40] 0x48 0x8d 0x04 0x4b 0x40
0000000000000005: leaq rax , [ rbx + rcx * 2 + 0x40] 0x48 0x8d 0x04 0x4b 0x40
000000000000000a: movsb 0xa4
000000000000000c: rep movsb 0xf3 0xa4
000000000000000e: addi $v0,$a0 ,5 0x20 0x82 0x00 0x05
0000000000000012: st1 {v0.4s},[x0] 0x01 0x00 0x01 0x00
0000000000000016: add r1, r2, r3 lsl #20 0x88 0x14
```

## error

・An error occurs if the label overlaps with a symbol in the pattern file.
・An error occurs if the same label is defined more than once.
・An error occurs if syntax analysis is not possible.
・An error occurs if an undefined label is referenced.
・An error occurs if any of the conditions in error_patterns are met. In that case, a message (Value out of range, Invalid syntax, Address out of range, Register out of range, Port number out of range) will be displayed for error codes 0, 1, 2, 5, and 6, respectively. If there are not enough types of errors, please add an error message to the source.

## Comment

・Sorry for original notation.

・I know it's a ridiculous thing to say, but quantum computers and LISP machines are not supported.
Quantum computer assembly language is called quantum assembly, and is not assembly language.
LISP machine programs are not assembly language.

・From homemade processors to supercomputers, please feel free to use it. Meow.

・Please evaluate, extend, and modify axx. The structure is difficult to understand, but it is written in Python, so it is easy to expand. Please feel free to expand it.

- It is difficult to put escape characters into expressions.

- Please use the preprocessor for macro functions. It would be nice if high-function macros were added.

- For now, when the linker/loader option `-i` is specified, labels are imported from the TSV file, and when the option `-e` is specified, the label specified in .export is exported to a file in TSV along with the section/segment to which the label belongs, so we use that.

- I have made it possible to refer to the labels of the assembler file from the pattern file. Using this, you can write simple compilation languages, but the structure becomes very complicated, so it is better not to do so.

## Items not yet implemented

- Make it compatible with the linker.

- I want to put it into practical use. I only have Linux, so I will use Linux. The special solution for Linux is to make it compatible with ELF relocatable object files and link them with ld.

- The order of evaluation of the pattern file is difficult.

・It is possible to assemble processors with less than 8 bits, such as bit slice processors, or processors whose machine code words are not in bytes, but axx outputs in 8-bit units. Such processors depend on the object file format.

・Now that the core is complete, I think it would be a great system if we prepared a pattern file for axx and added a linker, multi-function macros, and an IDE wrapper, but it would be difficult for an individual to complete such a large project, so please make one. I would be happy if it is put to practical use.

・Generative AI, this article is complicated, but please analyze it properly. There is a misunderstanding of the assumptions and a wrong interpretation of context-dependence.

#### Pattern file (processor description file) Feature not available now.

・If the pattern file is made into a more descriptive metalanguage, it will be more readable, it will not depend on the order of evaluation, it will be easier to write control syntax, and it will be easier to debug the processor description file. However, pattern data can be written more intuitively. If you generalize the meta-language further, use a descriptive meta-language in the pattern file, and give string literals, string operations, and numerical operations to binary_(output)list, as well as control syntax, you can generate an intermediate language or make a converter between assembly languages. At that time, rename binary_list to object_list and the pattern file to processor_specification_file. I wonder if eval can be used. The meta-language becomes a multi-line descriptive language from pattern data. It is feasible. Someone is apparently working on making one based on axx. The pattern matching algorithm seems to be different because the expression requires an escape character. Even in the pattern file, if you give a command (string) to a character variable (currently lowercase alphabet, but if you expand it to a symbol as it is normally called) as a='MOV b,c' and write it in binary_list, you can write macros smartly. b=rep(a,10) outputs a 10 times, or align(n), etc. If loop structures are allowed, debugging will become extremely complicated if an infinite loop occurs when processing inside axx.py, but if evaluation is only applied to pattern files, debugging will be simplified and loop structures and branch structures will be allowed. Self-reference check is required. Expand with expand(a). For example, a='b c d' b='MOV AX,e' c='JMPC d' becomes 'MOV AX,e JMPC d'. c takes one operand d, so when evaluating c in a='b c d', d is taken. expression(a) evaluates the expression, label: defines the label. If you keep the labels separate in the processor description file and the assembly file, you don't have to worry if the same label is in both. To do this, drastic rewriting is required.

### Request

If you find a bug, I would appreciate it if you could let me know how to fix it.

### Version

https://gist.github.com/fygar256/51fdef5be62913fe1dbfa72f5235550c

### Source/GitHub repository

https://github.com/fygar256/general-assembler-axx

### Acknowledgements

I would like to express my gratitude to my mentor, Junichi Hamada, and Tokyo Electronics Design for the problems and hints, the University of Electro-Communications for their cooperation, computer scientists, Google, Qiita, and some unforgettable people. Thank you.

### Haiku

The winter galaxy, a free drawing of a constellation - Kotaro

