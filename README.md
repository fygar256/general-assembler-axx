# GENERAL ASSEMBLER 'axx.py'

axx.py is a general assembler.

It is written in a general way, so the execution platform is not dependent on a specific processing system.

It is also set to ignore chr(13) at the end of lines in DOS files. I think it will work on any processing system that runs python.

I think axx has the ability to process the instruction set of any processor if you prepare pattern data, but it does not support the practical functions that a dedicated assembler has. The current version is an experimental implementation. I also intend to implement the practical functions of a dedicated assembler in the future.

・How to use

Use it like this: `python axx.py 8048.axx [sample.s]`.

axx reads assembler pattern data from the first argument and assembles the source file in the second argument based on the pattern data. If the second argument is omitted, the source is input from standard input.

In axx, assembly language source files and lines input from standard input are called assembly lines.

・Explanation of pattern data

Pattern data is arranged as follows.

```
"mnemonic" "operands" "error_patterns" "binary_list"
"mnemonic" "operands" "error_patterns" "binary_list"
"mnemonic" "operands" "error_patterns" "binary_list"
:
:
```

Mnemonic, operands, error_patterns, and binary_list must be enclosed in `""` (double quotes).

mnemonic can be omitted from the second line onwards. If omitted, specify a null string as "".

If omitted, the mnemonic from the previous line will be used.

operands may not be present. error_patterns can be omitted. binary_list cannot be omitted.

There are three types of pattern data:

```
(1) "mnemonic" "binary_list"
(2) "mnemonic" "operands" "binary_list"
(3) "mnemonic" "operands" "error_patterns" "binary_list"
```

・Comments

If you write "/" in the pattern file, the line after /* becomes a comment. Currently, it is not possible to close with */. Valid only after /* on that line.

・Case distinction, variables

The mnemonic in the pattern file is a character constant, so please write it in uppercase. The constant characters in operands should also be in uppercase. The assembly line will accept it as being the same in uppercase or lowercase.

The lowercase alphabets in operands, error_patterns, and binary_list are variables.

From operands, the value of the expression or symbol that corresponds to the variable position of the operand is assigned to the variable.

Lowercase letters a to n represent expressions, and o to z represent symbols. Values ​​are referenced from error_pattern and binary_list variables. A special variable in assembly line expressions is '$$', which represents the current location counter.

-Expression, Value

Error patterns and binary lists are evaluated in Python using the eval function. To reference variables, add a `#` as a prefix.

The assembly line value is evaluated using the built-in function expression in axx.py. Usually, symbols can be referenced, but for symbols with `%` or other prefixes, add a `#` as a prefix.

When passing a symbol value to .setsym in the pattern file, add a `#` as a prefix.

-error_patterns

error_patterns uses variables and comparison operators to specify the conditions for an error.

Multiple error patterns can be specified, separated by ','. Each element of error_patterns calls the python eval function.

For example, it looks like this:

```
"a>3;4,b>7;5"
```
In this example, if a>3, it returns error code 4, and if b>7, it returns error code 5.

・binary_list

binary_list specifies the codes to be output, separated by ','. For example, if you specify 0x03,#d, 0x3 will be output followed by d. The elements of binary_list call the python eval function to set the value.

Let's take 8048 as an example. If the pattern file contains

```
"ADD" "A,Rn" "n>7;5" "#n|0x68"
```

and you pass `add a,rn` to the assembly line, it will return error code 5 if n>7, and generate binary 0x69 with `add a,r1`.

・symbol

```
.setsym" "symbol" "n"
```

When you write this, symbol is defined with the value n.

Symbols include letters, numbers, etc., but axx uses the following characters as constituent characters of symbols: ` \t\n\0()[]{}\\`. This is called the termination character.

The termination character can be changed by writing the `.termc` command. The default is `\t\n\0 ()[]{}\\`.

```
".termc" "\t\n\0()[]{}\\"
```

Here is an example of the symbol definition z80. In a pattern file,

```
".setsym" "B" "0"
".setsym" "C" "1
".setsym" "D" "2
".setsym" "E" "3
".setsym" "H" "4
".setsym" "L" "5
".setsym" "A" "7
".setsym" "BC" "0x00"
".setsym" "DE" "0x10"
".setsym" "HL" "0x20"
".setsym" "SP" "0x30"
```

Writing the following in a pattern file will define the symbols B, C, D, E, H, L, A, BC, DE, HL, and SP as 0, 1, 2, 3, 4, 5, 7, 0x00, 0x10, 0x20, and 0x30, respectively. Symbols are not case sensitive.

If there are multiple definitions of the same symbol in a pattern file, the new one will replace the old one. That is,

```
".setsym" "B" "0"
".setsym" "C" "1"
"ADD" "A,s"

".setsym" "NZ" "0"
".setsym" "Z" "1"
".setsym" "NC" "2"
".setsym" "C" "3"
"RET" "s"
```

In this case, the C in ADD A,C is 1, and the C in RET C is 3.

・Example of symbols that contain a mixture of symbols, numbers, and letters

```
".setsym" "$s5" "21"
```

・Example of binary output

```
".setsym" "BC" "0x00"
".setsym" "DE" "0x10"
".setsym" "HL" "0x20"
"LD" "s,d" "(s&0xf!=0)||(s>>4)>3;9" "#s|0x01,#d&0xff,#d>>8"
```

Then, `ld bc,0x1234, ld de,0x1234, ld hl,0x1234` output `0x01,0x34,0x12, 0x11,0x34,0x12, 0x21,0x34,0x12`, respectively.

・Pattern order

```
(1) "LD" "A,(HL)"
(2) "LD" "A,d"
```

Pattern files are evaluated from top to bottom, so the one placed first takes precedence.

In this case, if (1) and (2) are reversed, ld a,(hl) in the assembly line will put (hl) in the value of d, so place LD A,(HL) in the pattern file before LD A,d. Place special patterns first and general patterns after.

・Floating point

For example, suppose there is a processor that includes floating point operands, and `MOVF fa,3.14` loads 3.14 into the fa register, with the opcode being 01. In this case, the pattern data is

```
"MOVF" "FA,d" "0x01,#d>>24,#d>>16,#d>>8,#d"
```

If you pass `movf fa,0f3.14` to the assemble line, the binary output will be 0x01,0xc3,0xf5,0x48,0x40.

-Number notation

Prefix binary numbers with '0b'.

Prefix hexadecimal numbers with '0x'.

Prefix floating-point float (32bit) with '0f'.

Prefix floating-point double (float 64bit) with '0d'.

-Error checking

Error checking is lax.

## Version

2024/02/21 First published

2024/07/30 Sorry, there was a bug.

2024/07/30 ver 1.0.0 released

2024/08/30 Documentation update

2024/09/12 Documentation update, floating point support version 1.0.1

2024/09/12 22:30 Special variable '$' to '$$'. version 1.0.2

2024/09/13 Add eval function. version 1.0.9

2024/09/13 15:14 Expanded eval function. Fixed pattern file syntax. version 1.1.0

2024/09/13 22:00 Revised symbol definition specifications. version 1.1.5

2024/09/14 Changed the way pattern files are written. Evaluation of errorpattern is now done with the eval function. version 1.2.0

2024/09/15 Symbols can now be defined by symbols. version 1.2.2

### Comments

- Please forgive any variations in notation.

- Obviously, LISP machines cannot be written.

### Thanks

I would like to express my gratitude to my mentor, Junichi Hamada, and Tokyo Denshi　Sekkei, who gave me problems and hints, the University of Electro-Communications　for their cooperation, and to some other unforgettable guys.
Thank you very much.
