## GENERAL ASSEMBLER 'axx.py'

axx.py is a generalized assembler.

It is written in a general way, so the execution platform is not dependent on a specific system.

It is also set to ignore chr(13) at the end of lines in DOS files. I think it will work on any processing system that runs python.

axx has the ability to process the instruction set of any processor if you prepare pattern data, but it does not support the practical functions of dedicated assemblers. The current version is an experimental implementation. I also intend to implement the practical functions of dedicated assemblers in the future.

・How to use

Use it as follows: `python axx.py 8048.axx [sample.s]`.

ax reads the assembler pattern data from the first argument and assembles the source file of the second argument based on the pattern data. If the second argument is omitted, the source is input from standard input.

In axx, a line input from an assembly language source file or standard input is called an assembly line.

・Pattern data explanation

Pattern data is arranged as follows.

```
mnemonic operands error_patterns binary_list
mnemonic operands error_patterns binary_list
mnemonic operands error_patterns binary_list
:
:
```

From the second line, mnemonic can be omitted by leaving it as a space. If omitted, the mnemonic from the previous line will be used.

All mnemonic must be specified except for spaces. operands may not be present. error_patterns can be omitted. binary_list cannot be omitted.

There are three types of pattern data:

```
(1) mnemonic binary_list
(2) mnemonic operands binary_list
(3) mnemonic operands error_patterns binary_list
```

・Comments

If you write '//' in the pattern file, the text after // on that line becomes a comment.

・Case distinction, variables

The mnemonic in the pattern file is a character constant, so write it in uppercase. The constant characters in operands should also be in uppercase. The assembly line accepts it as being the same in uppercase or lowercase.

Lowercase letters in operands, error_patterns, and binary_list are variables.

Please prefix variables in binary_list with '#'.

The expression or symbol value that corresponds to the variable's position in operands is assigned to the variable from operands.

Lowercase letters a through n represent expressions, and o through z represent symbols. Values ​​are referenced from error_pattern and variables in binary_list. A special variable in assembly line expressions is '$$', which represents the current location counter.

・error_patterns

error_patterns uses variables and comparison operators to specify the conditions that will cause an error.

Multiple error patterns can be specified, separated by ','.

For example, as follows.

```
a>3;4,b>7;5
```

In this example, when a>3, error code 4 is returned, and when b>7, error code 5 is returned.

・binary_list

binary_list specifies the code to be output, separated by ','. For example, if 0x03,#d is specified, d is output after 0x3. The elements of binary_list are set to values ​​by calling the eval function of Python.

Let's take 8048 as an example. If the pattern file contains

```
ADD A,Rn n>7;5 #n|0x68
```

, and `add a,rn` is passed to the assembly line, it will return error code 5 when n>7, and 0x69 will be generated with `add a,r1`.

・symbol

In the pattern file

```
$symbol=n
```

When you write this, the symbol is defined with the value n.

Let's take an example of z80. In the pattern file,

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

If you write these in the pattern file, the symbols B, C, D, E, H, L, A, BC, DE, HL, and SP will be defined as 0, 1, 2, 3, 4, 5, 7, 0x00, 0x10, 0x20, and 0x30, respectively. Symbols are not case sensitive.

If there are multiple definitions of the same symbol in the pattern file, the new one will replace the old one. That is,

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

In this case, the C in ADD A,C is 1, and the C in RET C is 3.

・Example of binary output

```
$BC=0x00
$DE=0x10
$HL=0x20
LD s,d (s&0xf!=0)||(s>>4)>3;9 #s|0x01,#d&0xff,#d>>8
```

So, ld bc,0x1234, ld de,0x1234, ld hl,0x1234 output 0x01,0x34,0x12, 0x11,0x34,0x12, 0x21,0x34,0x12, respectively.

・Order of patterns

Pattern files are evaluated from top to bottom, so the one placed first takes precedence.

```
(1) LD A,(HL)
(2) LD A,d
```

In this case, if (1) and (2) were reversed, ld a,(hl) in the assembly line would put (hl) in the value of d, so place LD A,(HL) in the pattern file before LD A,d. Place special patterns first and general patterns after.

- Floating point

For example, suppose there is a processor that includes floating point operands, and `MOVF fa,3.14` loads 3.14 into the fa register, with the opcode being 01. In this case, the pattern data is

```
MOVF FA,d 0x01,#d>>24&0xff,#d>>16&0xff,#d>>8&0xff,#d&0xff
```

If you pass `movf fa,0f3.14` to the assemble line, the binary output will be 0x01,0xc3,0xf5,0x48,0x40.

-Number notation

Prefix binary numbers with '0b'.

Prefix hexadecimal numbers with '0x'.

Prefix floating-point float (32bit) with '0f'.

Prefix floating-point double (float 64bit) with '0d'.

・Error check

Error check is not sufficient.

・Comment

Please forgive any inconsistencies in notation.

It goes without saying that you can't write a LISP machine.

### Thanks

I would like to express my gratitude to my mentor, Junichi Hamada, and Tokyo Electronics Design, who gave me problems and hints, the University of Electro-Communications, who cooperated with me, and to some other unforgettable guys. Thank you very much.
