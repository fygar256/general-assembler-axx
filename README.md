axx.py is a general purpose assembler that generalizes assembler.

・How to use
Use it like axx.py 8048.axx [ sample.asm ].
axx reads the assembler pattern data from the first argument and assembles the second argument source file based on the pattern data.
If you omit the second argument, input the source from standard input.

・Explanation of pattern data
The pattern data is
'command' 'operands' 'error_pattern' 'object_list'
If you omit the command with a space, the previous command will be used.
'command' must be specified unless it is a space.
There may be no operands. object_list must be specified. error_pattern can be omitted, so the type of pattern data is
(1) command object_list
(2) command operands object_list
(3) command operands error_pattern object_list
There are 3 types.

·comment
If you write '//' in the pattern file, the line after // becomes a comment.
-Uppercase/lowercase letters, variables
Please write the command in the pattern file in uppercase letters. Also capitalize the constant characters in operands.
Uppercase and lowercase letters are accepted as the same from the assembly line.

The lowercase letters in operands, error_pattern, and object_list are variables.
The value of the expression or symbol that corresponds to the lowercase alphabetic position in the operands is assigned to the variable. Lowercase letters a~n represent expressions, and o~z represent symbols. Reference variables in error_pattern and object_list.
The special variable in the expression is $, which represents the current location counter.
・error_pattern
error_pattern uses variables and comparison operators to specify the conditions that cause an error.
Multiple error_patterns can be specified, separated by ','.
For example:
a>3;4,b>7;5
In this example, when a>3, error code 4 is returned, and when b>7, error code 5 is returned.

・object_list
object_list specifies the codes to be output separated by ','. For example, if you enter 0x03,d, d will be stored after 0x3.
Taking 8048 as an example,
ADD A,Rn n>7;5 n|0x68
So, if we say ADD A,Rn, it will return error code 5 when n>7 and create an object with n|0x68. For example, given the line above, add a,r1 will output an object called 0x69.
・symbol
in the pattern file
$symbol=n
, symbol is defined by the value n.
Let's take the z80 as an example.
in the pattern file
$B=0
$C=1
$D=2
$E=3
$H=5
$L=6
$A=7
$BC=0x00
$DE=0x10
$HL=0x20
$SP=0x30
If we write the symbols B, C, D, E, H, L, A, BC, DE, HL, SP as 0, 1, 2, 3, 4, 5, 6, 7, 0x00, 0x10 respectively Define as ,0x20,0x30. Symbols are not case sensitive.

If there are multiple definitions of the same symbol in a pattern file, the new ones will override the old ones. That is,

$B=0
$C=1
ADD A,s

$NZ=0
$Z=1
$NC=2
$C=3
RET s

In this case, C in ADD A,C is 0, and C in RET C is 3.
・Example of object output
LD s,d (s&0xf!=0)||(s>>4)>3;9 s|0x01,d&0xff,d>>8
So, ld bc,0x1234, ld de,0x1234, ld hl,0x1234 output 0x01,0x34,0x12, 0x11,0x34,0x12, 0x21,0x34,0x12 respectively.

・Mnemonic order
(1) LD A,(HL)
(2) LD A,d
The pattern files are evaluated in order from the top, so the one placed first has priority.
In this case, if (1) and (2) are reversed, ld a,(hl) in the assembly line will put (hl) in the value of d, so LD A,(HL ) should be placed before LD A,d. Place special patterns first and general patterns last.

·Error checking
Error checking is poor.


