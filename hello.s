.export _hello,_start,len
        .org 0x401000
section .text
_start:
_hello:
        mov     edx, 0
        mov     eax, 1      ; sys_write (01)
        mov     edi, 1      ; stdout    (01)
        mov     edx,len:    ; length    (13)
        movq    esi, msg    ; address
        syscall
        mov     edi, 0      ; return 0
        mov     eax, 60     ; sys_exit
        syscall
msg:     .ascii      "hello, world\n"
len:     .equ     $$ - msg
endsection

