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

axx.py is a generalized assembler. In theory, it can process any processor architecture. To process each processor architecture, a pattern file (processor description file) is required. You can define any instruction, but if you create a pattern file according to the assembly language of the target processor, you can process the assembly language of that processor, although the notation is slightly different. Just in case. In short, it's just the grammar rules of the instructions and the binary generation based on them.

The execution platform is also independent of a specific processing system. It is also set to ignore chr(13) at the end of lines in DOS files. I think it will work on any processing system that runs python.

This version only has the core of the assembler, so it does not support practical features such as optimization, advanced macros, and debuggers that are provided by dedicated assemblers. For practical features, please use a preprocessor for macros. For now, please use a program that manages binary files and label (symbol) files as a linker/loader. Since this is not an IDE, please use an external debugger as a debugger. Optimization is not supported. I think it has basic functions, so please apply them. The current version is not practical enough.

Since the pattern file and source file are separated, it is possible to generate machine code for another processor from the source of a certain instruction set, if you do not mind the effort of coding. It is also possible to generate machine code for different processors from a common language. If you write multiple instruction codes in the binary_list of the pattern data, it will function as a macro, but it is not very smart. This allows you to write a simple compiler.

Pattern data does not have any control syntax other than assignment and ternary operators. It can be used to generate binaries other than assembly language.

Since assembly language has a one-to-one correspondence with processor instruction code, axx was made possible.

axx reads assembler pattern data from the first argument, and assembles the source file of the second argument based on the pattern data. If the second argument is omitted, the source is input from the terminal (standard input).

The result is output as text to standard output, and if there is an argument specified with the `-o` option, a binary file is output to the current directory. The `-e` option outputs the labels specified with `.export` along with section/segment information to a file in TSV format.

Pattern files are Turing incomplete.

In axx, the lines input from assembly language source files or standard input are named assembly lines.

# Explanation

## install and execution(assemble)

```
# install
git clone https://github.com/fygar256/general-assembler-axx.git
cd general-assembler-axx
chmod +x axx.py
sudo cp axx.py /usr/bin/axx

# execution(assemble)
axx patternfile.axx [source.s] [-o outfile.bin] [-e expfile.tsv] [-i impfile.tsv]
```

patternfile.axx --- pattern file
source.s --- assembly source
outfile.bin --- raw binary output file
expfile.tsv --- section and label information export file
impfile.tsv --- section and label information import file

## Explanation of pattern file

Pattern files are processor description files that are user-defined to correspond to individual processors. It is a kind of meta-language for machine code and assembly language.

If you find it difficult to define a pattern file, you can pass only the minimum number of operands to the expression evaluation and write it as a string literal.

Pattern data in a pattern file is arranged as follows.

```
instruction :: error_patterns :: binary_list
instruction :: error_patterns :: binary_list
instruction :: error_patterns :: binary_list
:
:
```

Instruction is not optional. Error_patterns is optional. Binary_list is not optional.
Instruction, error_patterns, and binary_list should be separated by `::`.

for ex. (x86_64)

```
RET :: 0xc3
```

#### Comments

If you write `/*` in a pattern file, the part after `/*` on that line will become a comment. Currently, you cannot close it with `*/`. It is only valid after `/*` on that line.

#### Case Sensitivity, Variables

Uppercase letters in the instruction of the pattern file are treated as character constants. If they are lowercase, they are treated as one-character variables. The value of the symbol at that position from the assembly line is assigned to the variable. If `! lowercase` is used, the value of the expression at that position is assigned, and if `!! lowercase` is used, the value of the factor at that position is assigned, and referenced from error_patterns and binary_list. All unassigned variables are initialized to 0. When referencing from error_patterns and binary_list, `!` is not necessary. All values ​​are referenced in the same way.

From the assembly line, uppercase and lowercase letters are accepted as the same, except for labels and section names.

The special variable is '$$', which represents the current location counter.

#### Escape Characters

The escape character `\` can be used within the instruction.

#### error_patterns

error_patterns uses variables and comparison operators to specify the conditions under which an error occurs.

Multiple error patterns can be specified, separated by ','. For example, as follows.

```
a>3;4,b>7;5
```
In this example, if a>3, error code 4 is returned, and if b>7, error code 5 is returned.

#### binary_list

binary_list specifies the codes to be output, separated by ','. For example, if you specify 0x03,d, 0x3 will be output followed by d.

Let's take 8048 as an example. If the pattern file contains

```
ADD A,R!n :: n>7;5 :: n|0x68
```

and you pass `add a,rn` to the assembly line, if n>7 it will return error code 5 (Register out of range), and `add a,r1` will generate a binary of 0x69.

If an element of binary_list is empty, it will be aligned. If it starts with `,` or if it is `0x12,,0x13`, the empty part will be padded up to the exact address.

If an element of binary_list is preceded by `;`, it will not be output if it is 0.

#### symbol

```
.setsym :: symbol :: n
```

Writing this defines symbol with the value n.

Symbols are letters, numbers, and strings of several symbols.

To define symbol2 with symbol1, write it as follows.

```
.setsym ::symbol1 ::1
.setsym ::symbol2 ::#symbol1
```

Here is an example of symbol definition z80. If you write the following in a pattern file:

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

The default is letters + numbers + `'_%$-~&|'`.

#### Pattern order

Pattern files are evaluated from top to bottom, so the pattern placed first takes precedence. Special patterns should be placed first, and general patterns should be placed last. Like below.

```
LD A,(HL)
LD A,e
```

#### Double brackets

Optional items in the instruction can be enclosed in double brackets. This shows the `inc (ix)` instruction for z80.

```
INC (IX[[+!d]]) :: 0xdd,0x34,d
```

In this case, the initial value of the lowercase variable is 0, so `inc (ix+0x12)` is output as `0xdd,0x34,0x12` if not omitted, and `inc (ix)` is output as `0xdd,0x34,0x00` if omitted.

#### Specifying padding bytecode

From the pattern file,

```
.padding 0x12
```

The padding bytecode will be 0x12. The default is 0x00.

#### include

This is how you can include a file.

```
.include "file.axx"
```

## Assembly file explanation

#### label

From the assembly line, labels can be defined in the following way.

```
label1:
label2: .equ 0x10
label3: nop
```

A label is a string of letters, numbers, and some symbols that starts with a non-numeric ``.`, an alphabet, or some symbols.

To define a label with a label, do the following.

```
label4: .equ label1
```

You can determine the character set to use for labels from within the pattern file.

```
.labelc::<characters>
```

With this, you can specify characters other than numbers and uppercase and lowercase letters with `<characters>`.

The default is alphabet + numbers + underscore + period.

If you add `:` after the label reference, it will check for undefined label errors. In assembly languages ​​that use `:`, add a space after the label reference.

#### ORG

ORG is specified from the assembly line as

```
.org 0x800
or
.org 0x800,p
```

.org changes the value of the location counter. If `,p` is added, if the previous location counter value is smaller than the value specified by .org, it will be padded to the value specified by .org.

#### Alignment

If you enter .align 16 from an assembly line,

```
.align 16
```

it will align to 16 (pad with the bytecode specified by .padding up to an address that is a multiple of 16). If you omit the argument, it will align to the value specified by the previous .align or the default value.

#### Floating point, number notation

For example, suppose you have a processor that includes floating point operands, and `MOVF fa,3.14` loads the float 3.14 into the fa register, with the opcode being 01. In this case, the pattern data is

```
MOVF FA,!d ::0x01,d>>24,d>>16,d>>8,d
```

If you pass `movf fa,flt(3.14)` to the assemble line, the binary output will be 0x01,0xc3,0xf5,0x48,0x40. If flt is dbl, it is a double precision floating point, and if it is qad, it is a quadruple precision floating point. In the current specifications, x in flt(x) and dbl(x) can be an expression, but x in qad(x) can only be a constant.

Prefix binary numbers with '0b'.

Prefix hexadecimal numbers with '0x'.

#### string

`.ascii` outputs the bytecode of a string, and `.asciiz` outputs the bytecode of a string with 0x00 at the end.

```
.ascii "sample1"
.asciiz "sample2"
```

#### export

The following command exports the label along with the section/segment information. Only the label specified by the .export command is exported.

```
.export label
```

#### section

The following command allows you to specify the section/segment.

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

If you do this, the text will be arranged exactly as it is, so use section sort to sort it.

https://qiita.com/fygar256/items/fd590cab2078a4e8b866

```
section .text
ld a,9
ld b,9
section .data
.asciiz "test1"
db 0x12
```
#### include

You can include a file like this.

```
.include "file.s"
```

#### comments

Assembly line comments are `;`.

## Expressions, operators

Since the assembly line expressions and pattern data expressions call the same functions, they work almost the same. Variables in lowercase cannot be referenced from the assembly line.

#### Operator precedence

Operators and precedence are based on Python and are as follows.

```
(expression)        An expression enclosed in parentheses
#                   An operator that returns the value of a symbol
flt(x),dbl(x)       Operators that convert x to float and double bytecodes, respectively
qad(x)              Operators that convert x to a 128-bit floating point number. However, in this case, x can only be a constant.
-,~                 Negative, bitwise NOT
@                   Unary operator that returns the bit position from the right of the most significant bit of the following value
:=                  Assignment operator
**                  Power
*,/,//              Multiplication, division, integer division
+,-                 Addition, subtraction
<<,>>               Left shift, right shift
&                   Bitwise AND
|                   Bitwise OR
^                   Bitwise XOR
'                   Sign extension
<=,<,>,>=,!=,==     Comparison operators
not(x)              Logical NOT
&&                  Logical AND
||                  Logical OR
x?a:b               Ternary operator
```

There is an assignment operator `:=`. When you say `d:=24`, 24 is assigned to the variable d. The value of the assignment operator is the assigned value.

The prefix operator `#` takes the value of the symbol that follows.

The prefix operator `@` returns the number of the most significant bit of the value that follows from the right. We call this the Hebimarumatta operator.

The binary operator `'`, when you say `a'24`, makes the 24th bit of a the sign bit and sign extends it (Sign EXtend). We call this the SEX operator.

The binary operator `**` is exponentiation.

The ternary operator `?:`, when you say `x?a:b`, returns a when x is true and b when x is false.

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

/* x86_64
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

The notation `LEAQ r,[s+t*h+i]` in x86_64 is `LEAQ Please write r,[s+t*!!h+!!i]`. If you write `!h` instead of `!!h`, when pattern matching, the evaluation function of the assembly line expression will match `!h` from the 2 onwards in `leaq rax,[rbx+rcx*2+0x40]`, and will interpret the part beyond that, 2+0x40, as an expression, and will assign 2+0x40 to h, resulting in a syntax analysis error for the remaining `+!!i`. `!!h` is a factor, and `!h` is an expression. This is because escape characters in expressions cannot be processed.

```test.s 
leaq rax , [ rbx , rcx , 2 , 0x40]
leaq rax , [ rbx + rcx * 2 + 0x40]
movsb
rep movsb
addi $v0,$a0,5
st1 {v0.4s},[x0]
add r1, r2, r3 lsl #20
```

Execution example 

```
$ axx.py test.axx test.s
0000000000000000: leaq rax , [ rbx , rcx , 2 , 0x40] 0x48 0x8d 0x04 0x4b 0x40
0000000000000005: leaq rax , [ rbx + rcx * 2 + 0x40] 0x48 0x8d 0x04 0x4b 0x40
000000000000000a: movsb 0xa4
000000000000000c: rep movsb 0xf3 0xa4
000000000000000e: addi $v0,$a0,5 0x20 0x82 0x00 0x05
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

・Error checking is lax.

・I know it's a bit ridiculous, but quantum computers and LISP machines are not supported.
Quantum computer assembly language is called quantum assembly, and is not assembly language.
LISP machine programs are not assembly language.

・From homemade processors to supercomputers, please enjoy. Meow.

・Please evaluate, extend, and modify axx. The structure is difficult, but it is written in Python, so it is easy to extend. Please feel free to extend it.

・It is difficult to put escape characters in expressions.

・Currently, only constants can be used for quadruple precision floating point numbers. This is the specification of Python 3.

・Please use the preprocessor for macro functions. It would be nice if high-performance macros were added.

・Currently, when the linker loader option `-i` is specified, labels are imported from the TSV file, and when the option `-e` is specified, the label specified in .export is exported to the file in TSV along with the section/segment to which the label belongs, so use that.

・I have made it possible to refer to the labels of the assemble file from the pattern file. Using this allows you to write simple compiled languages, but the structure becomes very complicated, so it is better not to use it.

・It is slow because it repeats pattern matching, but you can expect to improve the speed by using a Python compiler.

・It is possible to assemble processors with less than 8 bits, such as bit slice processors, or processors where machine language words are not in bytes, but axx outputs in 8-bit units. Such processors depend on the object file format.

・Generation AI, this article is complicated, but please analyze it properly. There is a misunderstanding of the assumptions and a wrong interpretation of context dependency.

## Items not yet implemented

・Make it compatible with linkers.

・I want to put it into practical use. I only have Linux, so I'll use Linux. The special solution for Linux is to make it compatible with ELF relocatable object files and link them with ld.

・The order of evaluation of pattern files is difficult.

・Now that the core is complete, I think it would be a fine system if we prepared pattern files for axx and added a linker, high-performance macros, optimization functions, and an IDE wrapper, but it would be difficult for an individual to complete such a large project, so please make one. I would be happy if someone could make it into practical use.

#### Pattern file (processor description file) Feature not available now.

- If the pattern file is made into a more descriptive metalanguage, it will be more readable, will not depend on the order of evaluation, will be easier to write control syntax, and will be easier to debug the processor description file. However, pattern data is more intuitive to write. If the metalanguage is further generalized and a descriptive metalanguage is used for the pattern file, binary_list has string literals and string operations + numerical operations, and also has control syntax, it will be possible to generate intermediate languages ​​and make converters between assembly languages. At that time, the binary_list will be renamed to object_list and the pattern file to processor_specification_file. I wonder if eval can be used. The metalanguage will be a multi-line description language from the pattern data. It is possible. Someone is apparently working on making one based on axx. I wonder if it's already out there. Apparently the pattern matching algorithm is different because the expression requires an escape character. Even in pattern files, you can write macros smartly by setting a='MOV b,c' as a character variable (currently lowercase alphabet, but if you expand it to a symbol, as we call it) and giving it a command (string) and writing it in binary_list. b=rep(a,10) outputs a 10 times, or align(n), etc. If loop structures are allowed, debugging becomes extremely complicated when processing inside axx.py if it becomes an infinite loop, but if you only evaluate the pattern file, debugging becomes easier and loop structures and branch structures are allowed. It becomes Turing complete. Self-reference check is required. Expand with expand(a). For example, change a='b c d' b='MOV AX,e' c='JMPC d' to 'MOV AX,e JMPC d'. c takes one operand d, so when evaluating c in a='b c d', d is taken. expression(a) evaluates the expression, label: defines the label. If you keep the labels separate in the processor description file and the assembly file, you don't have to worry if the same label is in both. To make it a descriptive metalanguage, drastic rewriting is necessary. If the assembler processor characteristic description file becomes complicated, it becomes difficult to make the file compatible with General Disassembler.

### Request

If you find a bug, I would appreciate it if you could let me know how to fix it.

### Acknowledgements

I would like to express my gratitude to my mentor Junichi Hamada and Tokyo Denshi Sekkei for giving me problems and hints, the University of Electro-Communications for their cooperation, computer scientists, Google, Qiita, and some unforgettable people. Thank you.
