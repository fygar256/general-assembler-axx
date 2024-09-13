GENERAL ASSEMBLER 'axx.py'

axx.py is a generalized assembler.

It is written in a general way, so the execution platform is not dependent on a specific processing system.

It is also set to ignore chr(13) at the end of lines in DOS files. I think it will work on any processing system that runs python.

Axx has the ability to process the instruction set of any processor if you prepare pattern data, but it does not support the practical functions of dedicated assemblers. The current version is an experimental implementation. I also intend to implement the practical functions of dedicated assemblers in the future.

・How to use

Use it as follows: python axx.py 8048.axx [sample.s].

ax reads the assembler pattern data from the first argument and assembles the source file of the second argument based on the pattern data. If the second argument is omitted, the source is input from standard input.

In axx, the lines input from an assembly language source file or standard input are named assembly lines.

・Pattern data explanation

Pattern data is arranged as follows.

```
mnemonic operands error_patterns binary_list
mnemonic operands error_patterns binary_list
mnemonic operands error_patterns binary_list
:
:
```

mnemonic can be omitted from the second line onwards by leaving it as a space. If omitted, the mnemonic from the previous line will be used.

mnemonic must be specified except when it is a space. operands may not be present. error_patterns can be omitted. binary_list cannot be omitted.

There are three types of pattern data:

```
(1) mnemonic binary_list
(2) mnemonic operands binary_list
(3) mnemonic operands error_patterns binary_list
```

・Comment

If '//' is written in the pattern file, the part after // on that line becomes a comment.

・Case sensitivity, variables

The mnemonic in the pattern file is a character constant, so please write it in uppercase. The constant characters in operands should also be in uppercase. The assembly line accepts uppercase and lowercase characters as the same.

Lowercase alphabets in operands, error_patterns, and binary_list are variables.

Prefix variables in binary_list with '#'.

The expression or symbol value that corresponds to the variable position in the operand is assigned to the variable in operands.

Lowercase letters a through n represent expressions, and o through z represent symbols. Values ​​are referenced from variables in error_pattern and binary_list. The special variable in assembly line expressions is '$$', which represents the current location counter.

・error_patterns

Error_patterns uses variables and comparison operators to specify the conditions that will cause an error.

Multiple error patterns can be specified, separated by ','.

For example, as follows.

```
a>3;4,b>7;5
```

In this example, if a>3, it returns error code 4, and if b>7, it returns error code 5.

・binary_list

binary_list specifies the code to be output, separated by ','. For example, if you specify 0x03,#d, d will be output after 0x3. The elements of binary_list are set to values ​​by calling the Python eval function.

Let's take 8048 as an example. If the pattern file contains

```
ADD A,Rn n>7;5 #n|0x68
```
, and you pass add a,rn to the assembly line, it will return error code 5 when n>7, and add a,r1 will generate the binary 0x69.

・symbol

If you write

```
.setsym symbol n
```

in the pattern file, symbol will be defined with the value n.

Here is an example of z80. If the pattern file contains

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

Writing this defines the symbols B, C, D, E, H, L, A, BC, DE, HL, and SP as 0, 1, 2, 3, 4, 5, 7, 0x00, 0x10, 0x20, and 0x30, respectively. Symbols are not case sensitive.

If there are multiple definitions of the same symbol in a pattern file, the new one will replace the old one. That is, if you have

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
then the C in ADD A,C will be 1, and the C in RET C will be 3.

Symbols consist of letters, numbers, and several symbols '$%@_'. Several symbols are defined in the source in axx.py.

・Example of a symbol that contains a mixture of symbols, numbers, and letters

```
.setsym $s5 21
```

・Example of binary output

```
.setsym BC 0x00
.setsym DE 0x10
.setsym HL 0x20
LD s,d (s&0xf!=0)||(s>>4)>3;9 #s|0x01,#d&0xff,#d>>8
```
so `ld bc,0x1234, ld de,0x1234, ld hl,0x1234` output `0x01,0x34,0x12, 0x11,0x34,0x12, 0x21,0x34,0x12`, respectively.

・Order of patterns

``
(1) LD A,(HL)
(2) LD A,d
``

Pattern files are evaluated from top to bottom, so the one placed first takes precedence.

In this case, if (1) and (2) are reversed, ld a,(hl) in the assembly line will put (hl) in the value of d, so place LD A,(HL) in the pattern file before LD A,d. Place special patterns first and general patterns after.

- Floating point

For example, suppose there is a processor that includes floating point as an operand, and MOVF fa,3.14 loads 3.14 into the fa register, with the opcode being 01. In that case, the pattern data would be

```
MOVF FA,d 0x01,#d>>24&0xff,#d>>16&0xff,#d>>8&0xff,#d&0xff
```

and if movf fa,0f3.14 is passed to the assembly line, the binary output will be 0x01,0xc3,0xf5,0x48,0x40.

・Number notation

Please prefix binary numbers with '0b'.

Please prefix hexadecimal numbers with '0x'.

Please prefix floating-point float (32bit) with '0f'.

Please prefix floating-point double (float 64bit) with '0d'.

・Error checking

Error checking is lax.
