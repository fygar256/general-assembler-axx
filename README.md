--- axx
title: General Assembler General Assembler 'axx
tags: Terminal Python general assembler
author: fygar256
slide: false
---tags: general assembler 'axx.py' tags: general assembler 'axx.py'

GENERAL ASSEMBLER 'axx.py'

Nickname is Paxx because it was written in python.

# Test environment

Arch linux terminal

# Main text

axx.py is a generalized general assembler.

It is not dependent on a particular platform or processor, and ignores the chr(13) at the end of the DOS file.

axx can handle processors of any architecture if you provide pattern data, but it does not support the practical features of a dedicated assembler. The current version is an experimental implementation. We intend to implement the practical features of a dedicated assembler in the future.

Also, since the pattern files are separated from the source files, it is possible to generate the machine language for a processor of another certain instruction set from the source files of one instruction set, if you do not consider the coding effort.

#### Usage.

Use `python axx.py patternfile.axx [sample.s] [-o outfile.bin]`.

axx reads the assembler pattern data from the first argument and assembles the second argument source file based on the pattern data. If the second argument is omitted, the source is input from the standard input.

The result is output as text on the standard output, or a binary file in the current directory if the argument is specified with the `-o` option.

In axx, a line input from an assembly language source file or standard input is named an assembly line.

## Explanation of pattern files

Pattern files are user-defined for individual processors.

The pattern data in a pattern file is arranged as follows.

``` instruction :: error_patterns
instruction :: error_patterns :: binary_list 
instruction :: error_patterns :: binary_list 
instruction :: error_patterns :: binary_list 
:
:
```

instruction is optional. error_patterns is optional. binary_list is optional.
instruction, error_patterns, and binary_list must be separated by `::`.

for ex. (x86_64)

```
RET ::: 0xc3
```

The two types of pattern data are as follows.

```
(1) instruction :: binary_list
(2) instruction :: error_patterns :: binary_list
```

#### Comments

If you write `/*` in a pattern file, the lines after `/*` become comments. Currently, it is not possible to close with `*/`. It is only valid after `/*` of the line.

#### case sensitive, variable

The uppercase case of INSTRUCTION in the pattern file is treated as a character constant. Lower case will be treated as a single-character variable. From the assembly line, the value of the factor, expression or symbol that hits that position in instruction is assigned to the variable and referenced from error_patterns and binary_list.

Lowercase letters a through g represent expressions, h through n represent factors such as constants, and o through z represent symbols. All unassigned variables have an initial value of 0.

From the assembly line, both upper and lower case letters are accepted as the same.

A special variable is '$$', which represents the current location counter.

#### Operator Precedence

The operators and precedence are as follows based on python

```
(expression)            Parenthesized expression
#                       operator that returns the value of symbol
-,~                     negative, bit NOT
@                       unary operator that returns the number of bits to the right of the highest bit of the subsequent value
:=                      assignment operator
**                      multiply by a power
*,//                    multiplication, integer division
+,-                     addition, subtraction
<<,>>                   Shift left, shift right
&                       bit AND
|                       bit OR
^                       bit XOR
'                       Sign Extension
<=,<,>,>=,! =,==        Comparison operator
not(x)                  Logical NOT
&&                      Logical AND
||                      Logical OR
````

There is a `:=` assignment operator. If `d:=24`, the variable d is assigned 24. The value that the assignment operator has is the value that was assigned.

The prefix operator `#` takes the value of the symbol that follows.

The `@` prefix operator `@` returns how many bits of digits the value that follows consists of. This is named the hebimarumatta operator.

The binary operator `'`, `a'24`, takes the 24th bit of a as the sign bit and sign extends (Sign EXtend) it. This is named the SEX operator.

The binary operator `**` is a power.

#### Escape Character

The escape character `\` can be used in instructions.

#### error_patterns

error_patterns uses variables and comparison operators to specify the conditions under which errors occur.

Multiple error patterns can be specified and are separated by ','. For example

```
a>3;4,b>7;5
```
In this example, if a>3, error code 4 is returned, and if b>7, error code 5 is returned.

#### binary_list

binary_list specifies the codes to be output, separated by ','. For example, 0x03,d means that d is output after 0x3.

Take 8048 as an example. If the pattern file contains

```
ADD A,Rn :: n>7;5 :: n|0x68
```

and pass `add a,rn` to the assembly line, it returns error code 5 if n>7, and `add a,r1` produces a binary of 0x69.

If the element of `binary_list` is empty, alignment is performed. If it starts with `,` or `0x12,,0x13`, etc., the empty part is padded to the exact address.

If an element of the binary_list starts with `;`, it will not be output if the element is zero.

#### symbol

```
.setsym :: symbol :: n
```

would define symbol with the value n.

A symbol is a sequence of letters, numbers, and some symbols.

To define symbol2 with symbol1, write the following.

````
.setsym ::symbol1 ::1
.setsym ::symbol2 ::#symbol1
```

Here is an example of z80 in the symbol definition. In the pattern file

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

is written to define the symbols B,C,D,E,H,L,A,BC,DE,HL,SP as 0,1,2,3,4,5,7,0x00,0x10,0x20,0x30 respectively. Symbols are case-insensitive.

If there are multiple definitions of the same symbol in the pattern file, the new one updates the old one. I.e.,

```
.setsym ::B::0
.setsym ::C::1
ADD A,s

.setsym ::NZ::0
.setsym ::Z::1
.setsym ::NC::2
.setsym ::C ::3
RET s
````
In this case, C in ADD A,C is 1 and C in RET C is 3.

Example of a symbol with mixed symbols, numbers, and alphabets

```
.setsym ::$s5:: 21
```

All symbols are cleared with ``.clearsym``.

```
.clearsym
```

From within the pattern file, you can determine the character set to use for the symbol.

```
.symbolc::<characters>
```

allows you to specify ``<characters>` for characters other than numbers and alphabetic uppercase and lowercase letters.

The default is alphabet + numbers + `'_%$-~&|'`.

#### Pattern Order

````
(1) LD A,(HL)
(2) LD A,d
```

Pattern files are evaluated from the top, so the first pattern placed first takes precedence. Place special patterns first and general patterns later.


#### double-big-brackets

The abbreviations in the instruction are enclosed in double quotes. z80's `inc (ix)` instruction is shown here.

```
INC (IX[[+d]]) :: 0xdd,0x34,d
```

In this case, the initial value of the lower-case variable is 0, so `inc (ix+0x12)` and `0xdd,0x34,0x12` if not omitted, or `inc (ix)` and `0xdd,0x34,0x00` if omitted.

#### Byte code specification for padding

From pattern file,

```
.padding 0x12
```

will result in a padding bytecode of 0x12. The default is 0x00.

## Assembly file description

#### label

From the assembly line, labels can be defined in the following way.

```
label1: .
label2: .equ 0x10
label3: nop
```

A label is a sequence of two or more alphabetic, numeric, and some symbols, beginning with a non-numeric `. `` or a sequence of two or more characters, alphabetic, numeric, and some symbols, beginning with a letter or some symbol.

Defining a label with a label is as follows.

```
label4: .equ label1
```

From within the pattern file, you can determine the character set to use for the label.

```
.labelc::<characters>
```

allows you to specify ``<characters>` except numbers and lower case alphabetic characters.

The default is alphabet + numbers + underscore. Only at the beginning of a label, `. `` is allowed.

#### ORG

ORG is from the assembly line,

```
.org 0x800
```
and the

#### Alignment

From the assembly line,

```
.align 16
```

will align at 16 (padding to addresses that are multiples of 16 with the byte code specified in .padding). If the argument is omitted, the alignment is done with the number specified in the previous .align or the default value.

#### Floating point and number notation

For example, suppose we have a processor with floating point as its operand, and `MOVF fa,3.14` loads 3.14 into the fa register and its opcode is 01. In that case, the pattern data is,

```
MOVF FA,d ::0x01,d>>24,d>>16,d>>8,d
```

and passing ``movf fa,0f3.14`` to the assembly line, the binary output will be 0x01,0xc3,0xf5,0x48,0x40.

Binary numbers must be prefixed with '0b'.

Hexadecimal numbers must be prefixed with '0x'.

Floating point float (32bit) should be prefixed with '0f'.

Floating point double (float 64bit) should be prefixed with '0d'.

#### String

Use ``.ascii`'' to output strings and ``.asciiz`'' to output the byte code of strings with trailing 0x00.

```
.ascii “sample1”
.asciiz “sample2”
```

#### Comments

Assembly line comments are `;`.

## Example of binary output.

```
.setsym:: BC:: 0x00
.setsym:: DE:: 0x10
.setsym:: HL:: 0x20
LD s,d:: (s&0xf!=0)||(s>>4)>3;9 :: s|0x01,d&0xff,d>>8
```

and `ld bc,0x1234, ld de,0x1234, ld hl,0x1234` output ``0x01,0x34,0x12, 0x11,0x34,0x12, 0x21,0x34,0x12` respectively.

### Test some instructions on some processors.

Since this is a test, the binary is different from the actual code.

test.axx

```test.axx
/* test
.setsym ::a:: 7
.setsym ::b:: 1
.setsym ::%% ::7
.setsym ::||::: 8
LD s,x :: 0x1,y,s,x

/* ARM64
.setsym ::r1 ::: 2
.setsym ::r2 ::: 3
.setsym ::r3 :: 4
.setsym ::lsl::: 6
ADD w, x, y z #d :: 0x88,d
ADD x, y, e :: 0x91,x,y,e

/* A64FX
.setsym ::v0 :: 0
.setsym ::x0 :: 1
ST1 {x.4S},[y] :: 0x01,x,y,0

/* MIPS
.setsym ::$s5 ::21
.setsym ::$v0 ::2
.setsym ::$a0 ::4
ADDI x,y,d :: (e:=(0x20000000|(y<<21)|(x<<16)|d&0xffff))>>24,e>>16,e>>8,e

/* x86_64
.setsym ::rax:: 0
.setsym ::rbx:: 3
.setsym ::rcx ::1
.setsym ::rep ::0xf3

MMX A,B :: ,0x12,0x13
LEAQ r,[s,t,d,e] :: 0x48,0x8d,0x04,((@d)-1)<<6|t<<3|s,e
LEAQ r, [ s + t * h + i ] :: 0x48,0x8d,0x04,((@h)-1)<<6|t<<3|s,i
[[z]] MOVSB :: ;z,0xa4
TEST :: 0x12,,0x13

/* ookakko test
LD (IX[[+d]]),(IX[[+e]]):: 0xfd,0x04,d,e 
NOP :: 0x01
````test.s

test.s

````test.s
leaq rax , [ rbx , rcx , 2 , 0x40].
leaq rax , [ rbx + rcx * 2 + 0x40].
movsb
rep movsb
addi $v0,$a0,5
st1 {v0.4s},[x0].
add r1, r2, r3 lsl #20

````

Execution example

```
$ axx.py test.axx test.s
00000000000000000000: leaq rax , [ rbx , rcx , 2 , 0x40] 0x48 0x8d 0x04 0x4b 0x40
0000000000000005: leaq rax , [ rbx + rcx * 2 + 0x40] 0x48 0x8d 0x04 0x4b 0x40
000000000000000a: movsb 0xa4
000000000000000c: rep movsb 0xf3 0xa4
0000000000000000000e: addi $v0,$a0,5 0x20 0x82 0x00 0x05
000000000000000012: st1 {v0.4s},[x0] 0x01 0x00 0x01 0x00
00000000000000000016: add r1, r2, r3 lsl #20 0x88 0x14
```

## Comment.

Sorry for original notation.

The error check is not so good. It is difficult to make undefined label error in the specification.

I was told that it is absurd, but it is not compatible with quantum computers and LISP machines.
The assembly language of the quantum computer is called quantum assembly, not assembly language.
The program of LISP machine is not assembly language.

Please try from homemade processors to supercomputers. Nyaha.

It is not compatible with runtime variable length byte instructions because it must be equipped with an emulator.

It is possible to assemble processors with less than 8 bits, e.g. bit-sliced processors, or processors where the machine word is not in bytes, but since the output of axx is in bytes, processing is required. Whether or not processing is required also depends on the specifications of the binary file format that may be implemented in the future.

The pattern data is written differently depending on the addressing mode.

Please evaluate and extend and fix this.

Please evaluate and extend and fix this. High readability. It is not dependent on the order of evaluation. It is difficult to distinguish between character constants and undefined labels in the pattern file method. Meta language is still better.

## Future issues

The order of evaluation of pattern files is difficult, so we need to do something about it.

Linker should be able to handle it.

More error checking.

Escape characters in expressions don't work.

Add a macro function.

Binary file format should be supported.

### Thanks

I would like to express my gratitude to my mentor, Junichi Hamada, and Tokyo Electronics Design, who gave me problems and hints, the University of Electro-Communications, who cooperated with me, and to some other unforgettable guys. Thank you very much.
