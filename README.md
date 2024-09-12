# GENERAL ASSEMBLER 'axx.py

axx.py is a general assembler that generalizes the assembler.

Because it is written in a general way, it does not depend on a particular execution platform or processor.

It also ignores chr(13) at the end of a line in a DOS file, so it should work on any system that runs python.

I believe axx has the ability to process any processor's instruction set if you provide pattern data, but it does not support the practical features that a dedicated assembler has. The current version is an experimental implementation. We intend to implement the practical features of a dedicated assembler in the future.

How to use

`python axx.py 8048.axx [sample.s]`

axx reads the assembler pattern data from the first argument and assembles the second argument source file based on the pattern data. If the second argument is omitted, the source is entered from standard input.

In axx, the line input from an assembly language source file or standard input is named an assembly line.

・Explanation of pattern data

The pattern data is arranged as follows.

```
mnemonic operands error_patterns binary_list 
mnemonic operands error_patterns binary_list 
mnemonic operands error_patterns binary_list 
:
:
```
.
mnemonic can be omitted from the second line by using a space. If it is omitted, the mnemonic of the previous line is adopted.

mnemonic must be specified except for a space. operands may not be present. error_patterns may be omitted. binary_list may not be omitted. binary_list : : : mnemonic must be specified except for a space.

There are three types of pattern data: (1 ) mnemonic binary

```
(1) mnemonic binary_list
(2) mnemonic operands binary_list
(3) mnemonic operands error_patterns binary_list
```

Comment

If '//' is written in the pattern file, the line after // becomes a comment.

Case sensitivity, variables

In the pattern file, mnemonic is a character constant, so it should be written in upper case, and the constant character in operands should also be in upper case. From the assembly line, both uppercase and lowercase are accepted as the same.

The lowercase alphabets in operands, error_patterns and binary_list are variables.

The variable is assigned the value of the expression or symbol that hits that position in operands.

Lowercase letters a through n represent expressions, o through z symbols, and values are referenced from the error_patterns and binary_list variables. The special variable for assembly line expressions is '$$', which represents the current location counter.

error_patterns

error_patterns uses variables and comparison operators to specify the conditions under which errors occur.

Multiple error patterns can be specified and are separated by ','.

For example

```
a>3;4,b>7;5
```

In this example, if a>3, error code 4 is returned, and if b>7, error code 5 is returned.

binary_list

binary_list specifies the codes to be output, separated by ','. For example, 0x03,d means that d is stored after 0x3.

Taking 8048 as an example, (1)

```
ADD A,Rn n>7;5 n|0x68
```

and ADD A,Rn will return error code 5 when n>7 and generate a binary with n|0x68. For example, given the above line, ADD A,R1 will output a binary of 0x69.

Eval

Elements of the binary_list can be evaluated for value by calling the python eval function.
Lower-case variables in the eval must be prefixed with '#'.

For example,

```
ADD A,Rn [#n|0x68]
```
has the same function as (1).

Symbol
In the pattern file

```
$symbol=n
```

in the pattern file, the symbol is defined with the value n.

Here is an example for z80. In the pattern file, write

```
$B=0
$C=1
$D=2
$E=3
$H=4
$L=5
$A=7
$BC=0x00
$DE=0x10
$HL=0x20
$SP=0x30
```

Write “$B,C,D,E,H,L,A,BC,DE,HL,SP” to define the symbols B,C,D,E,H,L,A,BC,DE,HL,SP as 0,1,2,3,4,5,7,0x00,0x10,0x20,0x30, respectively. Symbols are case-insensitive.

If there are multiple definitions of the same symbol in the pattern file, the new one updates the old one. I.e.,

```
$B=0
$C=1
ADD A,s

$NZ=0
$Z=1
$NC=2
$C=3
RET s
```

then C in ADD A,C is 1 and C in RET C is 3.

Example of Binary Output

```
LD s,d (s&0xf!=0)||(s>>4)>3;9 s|0x01,d&0xff,d>>8
```

and ld bc,0x1234, ld de,0x1234, and ld hl,0x1234 output 0x01,0x34,0x12, 0x11,0x34,0x12, and 0x21,0x34,0x12, respectively.

Pattern order

```
(1) LD A,(HL)
(2) LD A,d
```

The pattern files are evaluated in order from the top, so the one placed first takes precedence.

In this case, if (1) and (2) are reversed, the pattern file LD A,(HL) should be placed before LD A,d because the assembly line ld a,(hl) would put (hl) in the d value. Place the special pattern first and the general pattern after.

Floating point

For example, suppose there is a processor that contains floating point as its operand, and MOVF fa,3.14 loads 3.14 into the fa register and its opcode is 01. In that case, the pattern data is,

```
MOVF FA,d 01,d>>24&0xff,d>>16&0xff,d>>8&0xff,d&0xff
```

and if movf fa,0f3.14 is passed to the assembly line, the binary output will be 0x01,0xc3,0xf5,0x48,0x40.

Hexadecimal notation

Hexadecimal numbers must be prefixed with '0x'.
Floating point float (32bit) should be prefixed with '0f'.
Floating point double (float 64bit) should be prefixed with '0d'.

Error Checking

Error checking is not sufficient.

### Thanks

I would like to express my gratitude to my mentors, Junichi Hamada and Tokyo Denshi Sekkei, who gave me problems and hints, and to the University of Electro-Communications for their cooperation.
