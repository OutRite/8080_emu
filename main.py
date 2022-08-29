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
#memory.write_memory(0x0000, 0xc3, restricted=False)
#memory.write_memory(0x0001, 0x00, restricted=False)
#memory.write_memory(0x0002, 0x01, restricted=False)
#memory.write_memory(368, 0x07, restricted=False)
#memory.write_memory(0x059c, 0xc3, restricted=False)
#memory.write_memory(0x059d, 0xc2, restricted=False)
#memory.write_memory(0x059e, 0x05, restricted=False)
#cpu.display_enabled = False
#opcodes.cpm_mode = True

cpu.boot(0x0000)
