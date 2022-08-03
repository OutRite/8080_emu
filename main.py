import memory
import cpu

print("Space Invaders Emulator")

memory.load_file(0x0000, "invaders.h")
memory.load_file(0x0800, "invaders.g")
memory.load_file(0x1000, "invaders.f")
memory.load_file(0x1800, "invaders.e")

cpu.boot(0x0000)
