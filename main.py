import memory
import cpu
import opcodes

print("Space Invaders Emulator")

memory.reset_ram()
memory.load_file(0x0000, "invaders.h")
memory.load_file(0x0800, "invaders.g")
memory.load_file(0x1000, "invaders.f")
memory.load_file(0x1800, "invaders.e")

#memory.load_file(0x0100, "cpudiag.bin")
#cpu.display_enabled = False
#opcodes.cpm_mode = True

cpu.boot(0x0000)
