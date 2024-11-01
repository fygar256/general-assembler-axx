GENERAL ASSEMBLER 'axx.py'

It was written in python, so its nickname is Paxx.

# Test environment

Arch linux terminal

# Main text

axx.py is a general assembler that generalizes assemblers.

The execution platform is not dependent on a specific processing system. It is also set to ignore chr(13) at the end of lines in DOS files. I think it will work on any processing system that runs python.

axx can process any processor architecture if you prepare pattern data, but it does not support the practical functions that dedicated assemblers have. The current version is an experimental implementation. For practical functions, please use a preprocessor for macros. For the time being, please use a program that manages binary files and label (symbol) files as a linker/loader.

Since the pattern file and source file are separated, it is possible to generate machine code for another processor from the source of one instruction set, if you do not mind the effort of coding.

Pattern data does not have control syntax other than assignment. It can be used to generate binaries not limited to assembly language.

Axx was made possible because assembly language has a one-to-one correspondence with processor instructions.

Axx can be used to develop custom assemblers.

#### Usage

Use it like this: `python axx.py patternfile.axx [sample.s] [-o outfile.bin] [-e expfile.tsv] [-i impfile.tsv]`.

Axx reads assembler pattern data from the first argument and assembles the source file of the second argument based on the pattern data. If the second argument is omitted, input the source from the terminal (standard input).

The result is output as text to standard output, and if there is an argument specified with the `-o` option, a binary file is output to the current directory. The `-e` option outputs the label specified with `.export` to a file in TSV format.

In axx, the lines input from the assembly language source file or standard input are named assembly lines.

## Explanation of pattern files

Pattern files are user-defined to accommodate individual processors.

Pattern data in a pattern file is arranged as follows:

```
instruction :: error_patterns :: binary_list
instruction :: error_patterns :: binary_list
instruction :: error_patterns :: binary_list
:
:
```

Instruction cannot be omitted. Error_patterns can be omitted. Binary_list cannot be omitted.
Instruction, error_patterns, and binary_list should be separated by `::`.

for ex. (x86_64)

```
RET :: 0xc3
```

There are two types of pattern data:

```
(1) instruction :: binary_list
(2) instruction :: error_patterns :: binary_list
```

#### Comments

Writing `/*` in a pattern file makes the part after `/*` on that line a comment. Currently, you cannot close it with `*/`. It is only valid for the part after `/*` on that line.

#### Case sensitivity, variables

Uppercase letters in the instruction of the pattern file are treated as character constants. If they are lowercase, they are treated as one-character variables. The value of the symbol at that position from the assembly line is assigned to the variable. If `! lowercase` is used, the value of the expression at that position is assigned, and if `!! lowercase` is used, the value of the factor at that position is assigned, and they are referenced from error_patterns and binary_list. All unassigned variables are initialized to 0. When referencing from error_patterns and binary_list, `!` is not necessary. All values ​​are referenced in the same way.

The assembly line accepts uppercase and lowercase characters as the same, except for labels and section names.

The special variable is '$$', which represents the current location counter.

#### Escape characters

You can use the escape character `\` in the instruction.

#### error_patterns

error_patterns uses variables and comparison operators to specify the conditions under which an error occurs.

Multiple error patterns can be specified, separated by ','. For example, as follows.

```
a>3;4,b>7;5
```
In this example, if a>3, error code 4 is returned, and if b>7, error code 5 is returned.

#### binary_list

binary_list specifies the code to be output, separated by ','. For example, if 0x03,d is specified, d will be output after 0x3.

Let's take 8048 as an example. If the pattern file contains

```
ADD A,R!n :: n>7;5 :: n|0x68
```

and you pass `add a,rn` to the assembly line, if n>7 it will return error code 5, and if `add a,r1` is used it will generate binary 0x69

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

The default is alphabets + numbers + `'_%$-~&|'`.

#### Pattern order

Pattern files are evaluated from top to bottom, so the pattern placed earlier takes precedence. Special patterns are placed first, and general patterns are placed last. Like below.

```
LD A,(HL)
LD A,e
```

#### Double brackets

Optional items in the instruction can be enclosed in double brackets. Here is the `inc (ix)` instruction for the z80.

```
INC (IX[[+!d]]) :: 0xdd,0x34,d
```

In this case, the initial value of the lowercase variable is 0, so if you specify `inc (ix+0x12)`, `0xdd,0x34,0x12` will be output, and if you specify `inc (ix)`, `0xdd,0x34,0x00` will be output.

#### Specifying padding bytecode

From the pattern file,

```
.padding 0x12
```

The padding bytecode will be 0x12. The default is 0x00.

#### include

This is how you can include a file.

``
.include "file.axx"
```

## Explanation of assembly files

#### label

Labels can be defined from the assembly line in the following way.

```
label1:
label2: .equ 0x10
label3: nop
```

A label is a string of letters, numbers, and some symbols, starting with a non-numeric `.`, alphabet, or some symbol, and is two or more characters long.

To define a label with a label, do the following:

```
label4: .equ label1
```

You can determine the character set to be used for the label from within the pattern file.

```
.labelc::<characters>
```

You can specify characters other than numbers and uppercase and lowercase alphabets with `<characters>`.

The default is alphabet + numbers + underscore. `.` is only allowed at the beginning of the label.

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

#### String

`.ascii` outputs the bytecode of a string, and `.asciiz` outputs the bytecode of a string with 0x00 at the end.

```
.ascii "sample1"
.asciiz "sample2"
```

#### export

You can export a label as shown below. Only the label specified by the .export command will be exported.

```
.export label
```

#### section

You can specify a section as shown below.

```
section .text
```

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

Assembly line expressions and pattern data expressions are almost the same because they call the same functions. You can write labels in assembly lines. Pattern data can contain lowercase variables.

#### Operator precedence

The operators and precedence are as follows, based on Python

```
(expression)        An expression enclosed in parentheses
#                   An operator that returns the value of a symbol
-,~                 Negative, bitwise NOT
@                   A unary operator that returns the bit position from the right of the most significant bit of the following value
:=                  Assignment operator
**                  Exponentiation
*,//                Multiplication, integer division
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
```

`:=` is available as an assignment operator. If you enter `d:=24`, 24 will be assigned to the variable d. The value of the assignment operator is the assigned value.

The prefix operator `#` takes the value of the symbol that follows.

The prefix operator `@` returns the number of the most significant bit of the value that follows, from the right. We call this the Hebimarumatta operator.

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

The notation for `LEAQ r,[s+t*h+i]` in x86_64 is `LEAQ r,[s+t*!!h+!!i]`. If you write `!h` instead of `!!h`, the evaluation function for the formula will interpret the 2 in `leaq rax,[rbx+rcx*2+0x40]` as `!h`, and the part beyond that, 2+0x40, as the formula, and 2+0x40 will be substituted for h, leaving the remaining `+!!i` as a remainder, resulting in a syntax analysis error. `!!h` is a factor, and `!h' is a formula.

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
$ axx.py　test .axx test.s
0000000000000000: leaq rax , [ rbx , rcx , 2 , 0x40] 0x48 0x8d 0x04 0x4b 0x40
0000000000000005: leaq rax , [ rbx + rcx * 2 + 0x40] 0x48 0x8d 0x04 0x4b 0x40
000000000000000a: movsb 0xa4
000000000000000c: rep movsb 0xf3 0xa4
000000000000000e: addi $v0,$a0 ,5 0x20 0x82 0x00 0x05
0000000000000012: st1 {v0.4s},[x0] 0x01 0x00 0x01 0x00
0000000000000016: add r1, r2, r3 lsl #20 0x88 0x14
```

## error

An error occurs if the label overlaps with a symbol in the pattern file.
An error occurs if the same label is defined more than once.
An error occurs if syntax analysis is not possible.
An error occurs if an undefined label is referenced.
An error occurs if any of the conditions in error_patterns are met.

## Comments

-Sorry for original notation.

-I know it's a ridiculous request, but quantum computers and LISP machines are not supported.
The assembly language of quantum computers is called quantum assembly, and is not assembly language.
LISP machine programs are not assembly language.

-From homemade processors to supercomputers, please. Meow.

-Instructions whose machine code byte length changes during execution, such as those that require an emulator, are not supported.

-Please evaluate and extend and fix this.

-It is difficult to include escape characters in expressions.

-Please use the preprocessor for macro functions. It would be nice if high-function macros were added.

・When the linker loader option `-i` is specified, labels are imported from the TSV file, and when the option `-e` is specified, the labels specified with .export are exported to the file in TSV, so use that.

・It is possible to assemble processors that are less than 8 bits, such as bit slice processors, or processors whose machine language words are not in bytes, but axx outputs in 8-bit units. Such processors depend on the object file format.

・Now that the core is complete, I think it would be a fine system if we prepared a pattern file for axx and added a linker, multi-function macros, and an IDE wrapper, but that's a bit much. The rest is generic, so someone please make it. I'd be happy if it were put to practical use.

・If the pattern file is made into a meta-language, it is highly readable, does not depend on the order of evaluation, is easy to write control syntax, and makes it easier to debug the processor definition file. After all, a meta-language is better.

・If axx is generalized further and a meta-language is used, binary_list is given string literals and string operations + numerical operations, and also has control syntax, an intermediate language can be generated and a converter between assembly languages ​​can be made. A simple compiler can also be written. In that case, the name of binary_list is changed to object_list. I wonder if eval can be used. To do that, drastic rewriting is required. The meta-language becomes a multi-line description language from the pattern data. It is feasible. Someone may make one based on axx. A general disassembler could also be made by making the meta-language almost the same.

## Future issues

・Make it compatible with the linker.

・I want to put it into practical use. I only have Linux, so I'll use Linux. A specific solution for Linux is to make it compatible with ELF object files and link them with ld.

-The order of evaluation of pattern files is difficult.

### Thanks

I would like to express my gratitude to my mentor, Junichi Hamada, and Tokyo Denshi Sekkei, who gave me the problems and hints, to the University of Electro-Communications, IEEE, Qiita, Associate Professor Susumu Yamazaki, and to some other unforgettable guys. Thank you very much.
