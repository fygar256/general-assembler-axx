### GENERAL ASSEMBLER 'axx.py'

axx.py is a generalized assembler.

It is written in a general way so that the execution platform does not depend on a specific processor. chr(13) at the end of the line in the DOS file is also ignored.

I believe it has the ability to handle a pan-processor instruction set if you provide pattern data, but it does not support the fine-grained features of a processor-specific assembler. This is an experimental implementation. I intend to implement the practical fine features of a dedicated assembler in the future.

How to use

`python axx.py 8048.axx [sample.asm]`

axx reads the assembly pattern data from the first argument and assembles the second argument source file based on the pattern data. If the second argument is omitted, the source is entered from the standard input.

In axx, the line input from an assembly language source file or standard input is named an assembly line.

・Explanation of pattern data

Pattern data is lined up as follows.

```
mnemonic operands error_patterns object_list 
mnemonic operands error_patterns object_list 
mnemonic operands error_patterns object_list 
:
:
```
・mnemonic

mnemonic can be omitted from the second line by using a space. If it is omitted, the mnemonic of the previous line is adopted.

If mnemonic is omitted, the mnemonic of the previous line is adopted. mnemonic must be specified except for spaces. operands may be omitted. error_patterns may be omitted. object_list may not be omitted.

There are three types of pattern data:

```
(1) mnemonic                               object_list
(2) mnemonic   operands                    object_list
(3) mnemonic   operands   error_patterns   object_list
```
・Comment

If '//' is written in the pattern file, the line after // becomes a comment.

・Case sensitivity, variables

The mnemonic in the pattern file is a character constant, so it should be written in upper case, and the constant character in operands should also be in upper case. From the assembly line, uppercase and lowercase are accepted as the same.

The lowercase alphabets in operands, error_patterns and object_list are variables.

The variable is assigned the value of the expression or symbol that hits that position in operands.

The lowercase letters a through n represent expressions, o through z symbols, and the values are referenced from the error_patterns and object_list variables. The expression special variable in assembly line is '$$' and represents the current location counter.

・error_patterns

error_patterns uses variables and comparison operators to specify the conditions under which errors occur.

Multiple error patterns can be specified and are separated by ','.

For example

```
a>3;4,b>7;5
```

In this example, if a>3, error code 4 is returned, and if b>7, error code 5 is returned.

・object_list

object_list specifies the codes to be output, separated by ','. For example, 0x03,d means that d is stored after 0x3.

Take 8048 as an example,

```
ADD A,Rn n>7;5 n|0x68
```

ADD A,Rn will return error code 5 when n>7, and an object with n|0x68 will be created. For example, given the above line, ADD A,R1 will output an object named 0x69.

・symbol

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

Define the symbols B,C,D,E,H,L,A,BC,DE,HL,SP as 0,1,2,3,4,5,7,0x00,0x10,0x20,0x30, respectively. Symbols are case-insensitive.

If there are multiple definitions of the same symbol in the pattern file, the new one updates the old one.

I.e.,

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

Example of object output

```
LD s,d (s&0xf!=0)||(s>>4)>3;9 s|0x01,d&0xff,d>>8
```

and ld bc,0x1234, ld de,0x1234, ld hl,0x1234 output 0x01,0x34,0x12, 0x11,0x34,0x12, 0x21,0x34,0x12 respectively.

・command order

```
(1) LD A,(HL)
(2) LD A,d
```

The pattern files are evaluated in order from the top, so the one placed first takes precedence.

In this case, if (1) and (2) are reversed, ld a,(hl) in the assembly line would put (hl) in the value of d, so ld a,(hl) in the pattern file should be placed before ld a,d. Place the special pattern first and the general pattern after.

・Floating point

For example, suppose we have a processor with floating point as an operand, and `MOVF fa,3.14` loads 3.14 into the fa register, and its opcode is 01. In that case, the pattern data is,

```
MOVF FA,d 01,d>>24&0xff,d>>16&0xff,d>>8&0xff,d&0xff
```

and if `movf fa,0f3.14` is passed to the assembly line, the object output will be 0x01,0xc3,0xf5,0x48,0x40.


・Number notation

Hexadecimal numbers must be prefixed with '0x'.

Floating point float (32bit) must be prefixed with '0f'.

Floating point double (64bit) should be prefixed with '0d'.

・Error check

Error checking is not sufficient.

### Thanks

I would like to express my gratitude to my mentors, Junichi Hamada and Tokyo Denshi Sekkei, who gave me problems and hints, and to the University of Electro-Communications for their cooperation.

