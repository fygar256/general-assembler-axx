hello_world: .ascii "Hello world!"
            db  10
hello_world_len: .equ $$ - hello_world:

  .global _start:,_func1:,hello_world:

_start:
  mov rax, 1 ; sys_write
  mov rdi, 1
  mov rsi, hello_world:
  mov rdx, hello_world_len:
  syscall

_func1:
  mov rax, 60 ; sys_exit
  mov rdi, 0
  syscall

