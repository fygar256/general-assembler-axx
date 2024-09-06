GENERAL PURPOSE ASSEMBLER 'axx.py

axx.py is a general-purpose assembler that generalizes the assembler.

How to use

axx.py 8048.axx [sample.asm].

axx reads the assembler pattern data from the first argument and assembles the second argument source file based on the pattern data.

If the second argument is omitted, input the source from the standard input.

・Explanation of Pattern Data

The pattern data is as follows,

```
command operands error_pattern object_list 
```

The command can be omitted from the second line by inserting a space. If omitted, the command of the previous line is used.

command must be specified except for a space, operands may be omitted, error_pattern may be omitted, and object_list may not be omitted.

Hence,

The pattern data types are,

```
(1 ) command                              object_list
(1')                                      object_list
(2 ) command   operands                   object_list
(3 ) command   operands   error_pattern   object_list
```

There are four types of pattern data.

・Comment

If '//' is written in the pattern file, the line after // becomes a comment.

・Case, Variables

In pattern files, commands should be written in upper case, and constant letters in operands should also be uppercase.

From the assembly line, uppercase and lowercase are accepted as the same.

The lowercase alphabets in operands, error_pattern and object_list are variables.

The variable is assigned the value of the expression or symbol that hits that position in operands.

The lowercase letters from a to n represent expressions, from o to z symbols, and the values are referenced from the error_pattern and object_list variables.

The expression's special variable is $, which represents the current location counter.

・error_pattern

error_pattern uses variables and comparison operators to specify the conditions under which errors occur.

Multiple error_patterns can be specified and should be separated by ','.

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

Then, ADD A,Rn would return error code 5 when n>7, and an object with n|0x68 would be created.

For example, given the above line, ADD A,R1 will output an object named 0x69.

・symbol

In the pattern file

```
$symbol=n
```

in the pattern file, the symbol is defined with the value n.

Here is an example for z80.

In the pattern file, write

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

・Example of object output

```
LD s,d (s&0xf!=0)||(s>>4)>3;9 s|0x01,d&0xff,d>>8
```

and ld bc,0x1234, ld de,0x1234, ld hl,0x1234 output 0x01,0x34,0x12, 0x11,0x34,0x12, 0x21,0x34,0x12 respectively.

・Mnemonic order

```
(1) LD A,(HL)
(2) LD A,d
```

The pattern files are evaluated in order from the top, so the one placed first takes precedence.

In this case, if (1) and (2) are reversed, ld a,(hl) in the assembly line would put (hl) in the value of d, so ld a,(hl) in the pattern file should be placed before ld a,d.

Place special patterns first and general patterns after.

・Hexadecimal number in assembly line

Write hexadecimal number with prefix 0x in assembly line to pass it.

```
ld a,0x12
```

Error Checking

Error checks are not thorough enough.


Translated with DeepL.com (free version)
