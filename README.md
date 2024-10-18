---
title: General Assembler 'axx'
tags: Terminal Python general assembler
author: fygar256
slide: false
---
GENERAL ASSEMBLER 'axx.py'

I wrote it in python, so the nickname is Paxx.

# Test environment

Arch linux terminal

# Main text

axx.py is a general assembler that generalizes assemblers.

The execution platform is not dependent on a specific processing system. It is also set to ignore chr(13) at the end of lines in DOS files. I think it will work on any processing system that runs python.

I think axx can process any processor if you prepare pattern data, but it does not support the practical functions that a dedicated assembler has. The current version is a trial implementation. I also intend to implement the practical functions of a dedicated assembler in the future.

Also, because the pattern file is separate from the source file, it is possible to generate machine code for a processor with a different instruction set from a source file with one instruction set, if you don't mind the effort of coding.

#### Usage

Use it like this: `python axx.py patternfile.axx [sample.s] [-o outfile.bin]`.

axx reads assembler pattern data from the first argument, and assembles the source file of the second argument based on the pattern data. If the second argument is omitted, the source is input from the standard input.

The result is output as text to the standard output, and if there is an argument specified with the `-o` option, a binary file is output to the current directory.

In axx, the assembly language source file or the line input from the standard input is named an assembly line.

#### Explanation of pattern data

The pattern data in the pattern file is arranged as follows:

```
instruction error_patterns binary_list
instruction error_patterns binary_list
instruction error_patterns binary_list
:
:
```

Instruction cannot be omitted. Error_patterns can be omitted. Binary_list cannot be omitted.

Enclose instruction in `"`.

for ex. (x86_64)

```
"RET" 0xc3
```

There are two types of pattern data:

```
(1) instruction binary_list
(2) instruction error_patterns binary_list
```

#### Comments

Writing `/*` in a pattern file makes the part after `/*` on that line a comment. Currently, you cannot close it with `*/`. It is only valid for the part after `/*` on that line.

Assembly line comments are `;`.

#### Case sensitivity, variables

Uppercase letters in the instruction in the pattern file are treated as character constants. Lowercase letters are treated as one-character variables. The value of the factor, expression, or symbol that corresponds to that position in the instruction is assigned to the variable from the assembly line, and is referenced from error_patterns and binary_list.

Lowercase letters a through g represent expressions, h through n represent factors such as constants, and o through z represent symbols. All variables that are not assigned have a default value of 0.

Uppercase and lowercase letters are accepted by the assembly line as the same.

The special variable is '$$', which represents the current location counter.

#### Operator precedence

The operators and precedence are based on Python and are as follows

```
(expression)         An expression enclosed in parentheses
#                    An operator that returns the value of a symbol
-,~                  Negative, bitwise NOT
@                    A unary operator that returns the number of bits from the right of the most significant bit of the value that follows
:=                   Assignment operator
**                   Power
*,//                 Multiplication, integer division
+,-                  Addition, subtraction
<<,>>                Left shift, right shift
&                    Bitwise AND
|                    Bitwise OR
^                    Bitwise XOR
'                    Sign extension
<=,<,>,>=,!=,==      Comparison operators
not(x)               Logical NOT
&&                   Logical AND
||                   Logical OR
```

There is an assignment operator `:=`. If you enter `d:=24`, 24 will be assigned to the variable d. The value of the assignment operator is the assigned value.

The prefix operator `#` takes the value of the symbol that follows.

The prefix operator `@` returns the number of bits of the value that follows. We call this Hebimarumatta operator.

The binary operator `'`, if you enter `a'24`, the 24th bit of a will be made the sign bit and sign extended (Sign EXtend). We call this the SEX operator.

The binary operator `**` is exponentiation.

#### Escape character

You can use the escape character `\` in the instruction.

#### error_patterns

error_patterns uses variables and comparison operators to specify the conditions under which an error occurs.

You can specify multiple error patterns, separated by ','. For example, as follows.

```
a>3;4,b>7;5
```
In this example, if a>3, error code 4 is returned, and if b>7, error code 5 is returned.

#### binary_list

binary_list specifies the code to be output, separated by ','. For example, if you specify 0x03,d, 0x3 will be output followed by d.

Let's take 8048 as an example. If the pattern file contains

```
"ADD A,Rn" n>7;5 n|0x68
```

and you pass `add a,rn` to the assembly line, if n>7 it will return error code 5, and if `add a,r1` is used it will generate binary 0x69

If an element of binary_list is empty, it will be aligned. If you start with `,` or use `0x12,,0x13`, the empty part will be padded to the exact address.

#### symbol

```
.setsym symbol n
```

Writing this defines a symbol with the value n.

Symbols are letters, numbers, or strings of several symbols.

To define symbol2 with symbol1, write it as follows.

```
.setsym symbol1 1
.setsym symbol2 #symbol1
```

Here is an example of symbol definition z80. In a pattern file,

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

Writing this will define the symbols B, C, D, E, H, L, A, BC, DE, HL, and SP as 0, 1, 2, 3, 4, 5, 7, 0x00, 0x10, 0x20, and 0x30, respectively. Symbols are not case sensitive.

If there are multiple definitions of the same symbol in a pattern file, the new one will replace the old one. That is,

```
$B=0
$C=1
"ADD A,s"

$NZ=0
$Z=1
$NC=2
$C=3
"RET s"
```
In this case, the C in ADD A,C is 1, and the C in RET C is 3.

・Example of a symbol that contains a mixture of symbols, numbers, and letters

```
.setsym $s5 21
```

Use `.clearsym` to clear all symbols.

```
.clearsym
```

#### Example of binary output

```
.setsym BC 0x00
.setsym DE 0x10
.setsym HL 0x20
"LD s,d" (s&0xf!=0)||(s>>4)>3;9 s|0x01,d&0xff,d>>8
```

Then, `ld bc,0x1234, ld de,0x1234, ld hl,0x1234` output `0x01,0x34,0x12, 0x11,0x34,0x12, 0x21,0x34,0x12`, respectively.

#### Pattern order

```
(1) "LD A,(HL)"
(2) "LD A,d"
```

Pattern files are evaluated from top to bottom, so the one placed first takes precedence. Special patterns are placed first, and general patterns are placed last.

#### Double brackets

Optional in instruction can be enclosed in double brackets. This shows the `inc (ix)` command of the z80.

```
"INC (IX[[+d]])" 0xdd,0x34,d
```

In this case, the initial value of the lowercase variable is 0, so if `inc (ix+0x12)` is not omitted, `0xdd,0x34,0x12` is output, and if `inc (ix)` is omitted, `0xdd,0x34,0x00` is output.

#### label

Labels can be defined from the assembly line in the following way.

```
label1:
label2: .equ 0x10
label3: nop
```

A label is a string of letters, numbers, and symbols, starting with a non-numeric character `.`, an alphabet, or some other symbol, and is two or more characters long.

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

If you set

```
.padding 0x12
```

from the pattern file, the padding bytecode will be 0x12. The default is 0x00.

If you set

```
.align 16
```

from the assemble line, the alignment will be 16.

### Floating point, number notation

For example, suppose you have a processor that includes floating point operands, and `MOVF fa,3.14` loads 3.14 into the fa register, with the opcode being 01. In that case, the pattern data is

```
"MOVF FA,d" 0x01,d>>24,d>>16,d>>8,d
```

And if you pass `movf fa,0f3.14` to the assemble line, the binary output will be 0x01,0xc3,0xf5,0x48,0x40.

Prefix binary numbers with '0b'.

Prefix hexadecimal numbers with '0x'.

Prefix floating point float (32bit) with '0f'.

For floating-point doubles (float 64bit), prefix them with '0d'.

### Tests of some instructions on some processors

This is a test, so the binary is different from the actual code.

```test.axx 
/* ARM64
.setsym r1 2
.setsym r2 3
.setsym r3 4
.setsym lsl 6
"ADD w, x, y z #d" 0x88,d

/* A64FX
.setsym v0 0
.setsym x0 1
"ST1 {x.4S},[y]" 0x01,x,y,0

/* MIPS
.setsym $s5 21
.setsym $v0 2
.setsym $a0 4
"ADDI x,y,d" (e:=(0x20000000|(y<<21)|(x<<16)|d&0xffff))>>24,e>>16,e>>8,e

/* x86_64
.setsym rax 0
.setsym rbx 3
.setsym rcx 1
"LEAQ r,[s,t,d,e]" 0x48,0x8d,0x04,((@d)-1)<<6|t<<3|s,e
"LEAQ r,[ s + t * h + i ]" 0x48,0x8d,0x04,((@h)-1)<<6|t<<3|s,i
```

```test.s 
leaq rax , [ rbx , rcx , 2 , 0x40] 
leaq rax , [ rbx + rcx * 2 + 0x40] 
addi $v0,$a0,5 
st1 {v0.4s},[x0] 
add r1, r2, r3 lsl #20 
``` 

Execution example

```
$ axx.py test.axx test.s 
0000000000000000:leaq rax , [ rbx , rcx , 2 , 0x40] 0x48 0x8d 0x04 0x40 0x40 
0000000000000005:leaq rax , [ rbx + rcx * 2 + 0x40] 0x48 0x8d 0x04 0x40 0x40 
000000000000000a:addi $v0,$a0,5 0x20 0x00 0x00 0x05 
000000000000000e:st1 {v0.4s},[x0] 0x01 0x00 0x00 0x00
0000000000000012:add r1, r2, r3 lsl #20 0x88 0x14
```

### Comments

・Sorry for original notation.

・Error checking is lax.

・I know it sounds ridiculous, but quantum computers and LISP machines are not supported. The assembly language of quantum computers is called quantum assembly, and is not assembly language.
The programs of LISP machines are not assembly language.

・From homemade processors to supercomputers, please enjoy. Meow.

・Since an emulator must be installed, run-time variable-length byte instructions are not supported.

・It is possible to assemble processors with less than 8 bits, such as bit slice processors and processors whose machine code words are not in byte units, but the output must be slightly processed.

・The pattern data is written differently depending on the addressing mode.

・Please evaluate and extend and fix this.

・If the pattern file is made into a meta-language, it will be easier to check for errors. It is highly readable. It will not depend on the order of evaluation. It will also be easier to check the binary [Do not output] item.

## Future issues

・The order of evaluation of the pattern file is difficult, so we will do something about it.

・Make it possible for the linker to handle it.

・Perform some more error checking.

・The escape character in the expression does not work, so we would like to solve it.

・Instructions with x86_64 prefixes must be split into two lines, so we would like to solve this. →If there is a macro function, this will be solved.

・We would like to add a macro function. Adding macros will make it truly GENERAL.

・Supports binary file formats. Depending on the specifications of the binary file, it can also support bit slices of less than 8 bits and processors whose word length is not in bytes.

## Request

Please let me know if you find any bugs. I'll do my best to fix them.
Please evaluate and extend and fix this.

## Acknowledgements

I would like to express my gratitude to my mentor, Junichi Hamada, and Tokyo Denshi Sekkei, who gave me the problems and hints, to the University of Electro-Communications, who cooperated with me, IEEE, Qiita, and to some other unforgettable guys. Thank you very much.

  
