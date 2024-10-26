GENERAL ASSEMBLER 'axx.py'

Nickname is Paxx because it was written in python.

# Test environment

Arch linux terminal

# Main text

axx.py is a generalized general assembler.

Pattern data has no control syntax except assignment. It can be used for binary generation as well as assembly language.

It also ignores chr(13) at the end of a line in a DOS file. py works on any system that runs python.

axx can handle processors of any architecture if you provide pattern data, but it does not support the practical features of a dedicated assembler. The current version is an experimental implementation. For practical functions, macros should be used with a preprocessor, and linker/loaders should be used with programs that process binary and label (symbol) files. The label value in the label file is an offset value from the beginning of the binary file. For now, we are exporting and importing labels.

Also, since the pattern file is separated from the source file, you can generate the machine language of the processor of another certain instruction set from the source file of one instruction set, if you do not consider the coding effort.

#### Usage.

Use `python axx.py patternfile.axx [sample.s] [-o outfile.bin] [-e expfile.tsv] [-i impfile.tsv]`.

axx reads the assembler pattern data from the first argument and assembles the second argument source file based on the pattern data. If the second argument is omitted, the source is input from the standard input.

The result is output as text on the standard output, or a binary file in the current directory if the `-o` option is specified as an argument. The `-l` option outputs the labels specified in `.global` to a file in TSV format.

In `axx', a line that is input from an assembly language source file or standard input is named an assembly line.

## Explanation of pattern files

Pattern files are user-defined for individual processors.

The pattern data in a pattern file is arranged as follows.

```
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


#### escape characters

The escape character `\` can be used in instruction.

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

```
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
```
In this case, C in ADD A,C is 1 and C in RET C is 3.

Example of a symbol with mixed symbols, numbers, and alphabets

```
.setsym ::$s5:: 21
```

Symbols are cleared with ``.clearsym``.

```
.clearsym::ax
```

The above example undefines the symbol ``ax``.

Clearing the entire symbol is done with no arguments.

```
.clearsym
```

From within the pattern file, you can determine the character set to use for the symbol.

```
.symbolc::<characters>
```

allows you to specify ``<characters>`` for characters other than numbers and alphabetic uppercase and lowercase letters.

The default is alphabet + numbers + `'_%$-~&|'`.

#### Pattern Order

```
(1) LD A,(HL)
(2) LD A,d
```

Pattern files are evaluated from the top, so the pattern placed first takes precedence. Place special patterns first and general patterns last.

#### Double brackets

Optional items in the instruction can be enclosed in double brackets. Here is the z80 `inc (ix)` instruction.

```
INC (IX[[+d]]) :: 0xdd,0x34,d
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

A label is a string of letters, numbers, and some symbols, starting with a non-numeric ``.`, alphabet, or some symbol, and has two or more characters.

To define a label with a label, do the following.

```
label4: .equ label1
```

You can determine the character set to be used for the label from within the pattern file.

```
.labelc::<characters>
```

You can specify characters other than numbers and uppercase and lowercase alphabets with `<characters>`.

The default is alphabet + numbers + underscore. `.` is only allowed at the beginning of the label.

If you add `:` after the label reference, it will check for undefined label errors. For assembly languages ​​that use `:`, put a space after the label reference.

#### ORG

ORG is set to

```
.org 0x800
```

from the assembly line.

#### Alignment

Setting

```
.align 16
```

from the assembly line will align to 16 (pad with bytecode specified by .padding up to an address that is a multiple of 16). If the argument is omitted, alignment will be set to the number specified by the previous .align or the default value.

#### Floating point, number notation

For example, suppose you have a processor that includes floating point operands, and `MOVF fa,3.14` loads 3.14 into the fa register, with the opcode being 01. In this case, the pattern data is

```
MOVF FA,d ::0x01,d>>24,d>>16,d>>8,d
```

If you pass `movf fa,0f3.14` to the assemble line, the binary output will be 0x01,0xc3,0xf5,0x48,0x40.

Prefix binary numbers with '0b'.

Prefix hexadecimal numbers with '0x'.

Prefix floating-point float (32bit) with '0f'.

Prefix floating-point double (float 64bit) with '0d'.

#### Strings

`.ascii` outputs the bytecode of a string, and `.asciiz` outputs the bytecode of a string with a 0x00 at the end.

```
.ascii "sample1"
.asciiz "sample2"
```

#### include

You can include a file like this.

```
.include "file.s"
```

#### export

You can specify a label to export like this. Only the label specified by the .export command will be exported.

```
.export label
```

#### section

You can specify the section as follows.

```
.section .text
```

#### section sort

For example,

```
.section .text
ld a,9
.section .data
.asciiz "test1"
.section .text
ld b,9
.section .data
db 0x12
```

If you do this, the text will be arranged exactly as it is, so use section sort to sort it.

Use like this: `chmod +x secsort.py` and `./secsort.py infile.s >outfile.s`

```
.section .text
ld a,9
ld b,9
.section .data
.asciiz "test1"
db 0x12
```

#### comment

Assembly line comments are `;`.

## Operators

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
^                 Bitwise XOR
'                 Sign extension
<=,<,>,>=,!=,==   Comparison operators
not(x)            Logical NOT
&&                Logical AND
||                Logical OR
```

There is an assignment operator `:=`. If you enter `d:=24`, 24 will be assigned to the variable d. The value of the assignment operator is the assigned value.

The prefix operator `#` takes the value of the symbol that follows.

The prefix operator `@` returns the number of the most significant bit of the value that follows, from the right. We call this the Hebimarumatta operator.

The binary operator `'`, for example `a'24`, sign extends (Sign EXtends) the 24th bit of a as the sign bit. We call this the SEX operator.

The binary operator `**` is exponentiation.

## Example of binary output

```
.setsym:: BC:: 0x00
.setsym:: DE:: 0x10
.setsym:: HL:: 0x20
LD s,d:: (s&0xf!=0)||(s>>4)>3;9 :: s|0x01,d&0xff,d>>8
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
[[z]] MOVSB ​​:: ;z,0xa4
TEST :: 0x12,,0x13

/* ookakko test
LD (IX[[+d]]),(IX[[+e]]):: 0xfd,0x04,d,e
NOP :: 0x01
```

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

``` $ axx.py test.axx test.s
0000000000000000: leaq rax , [ rbx , rcx , 2 , 0x4 0] 0x48 0x8d 0x04 0x4b 0x40
0000000000000005: leaq rax , [ rbx + rcx * 2 + 0x40] 0x48 0x8d 0x04 0x4b 0x40
000000000000000a: movsb 0xa4
000000000000000c: rep movsb 0xf3 0xa4
000000000000000e: addi $v0,$a0,5 0x20 0x82 0x00 0x05
0000000000000012: st1 {v0.4s},[x0] 0x01 0x00 0x01 0x00
0000000000000016: add r1, r2, r3 lsl #20 0x88 0x14
```

## Comments

・Sorry for original notation.

・Error checking is poor.

・I know it's a ridiculous request, but quantum computers and LISP machines are not supported.
Quantum computer assembly language is called quantum assembly, and is not assembly language.
LISP machine programs are not assembly language.

・From homemade processors to supercomputers, please feel free to use it. Meow.

・Since an emulator must be installed, run-time variable-length byte instructions are not supported.

・Please evaluate and extend and fix this.

・If you make the pattern file a meta-language, it is easier to check for errors. It is highly readable. It is not dependent on the order of evaluation. It is easy to write control syntax. It is easier to debug processor definition files. After all, a meta-language is better.

・Use a preprocessor for the macro function.

・If you specify the linker/loader option `-i`, labels will be imported from the TSV file, and if you specify the option `-e`, global labels will be output to the file in TSV, so use that.

- It is possible to assemble processors with less than 8 bits, such as bit slice processors, or processors where the machine language words are not in bytes, but since the axx output is in bytes, processing is required.

## Future issues

- Make it compatible with the linker.

- The order of evaluation of the pattern file is difficult, so we will do something about it.

- Do more error checking.

- Escape characters in expressions do not work, so we would like to solve this.

### Thanks

I would like to express my gratitude to my mentor, Junichi Hamada, and Tokyo Denshi Sekkei, who gave me the problems and hints, to the University of Electro-Communications, IEEE, Qiita, Associate Professor Susumu Yamazaki, and to some other unforgettable guys. Thank you very much.
