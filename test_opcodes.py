import cpu
import memory


def test_mov():
    memory.reset_ram()
    memory.registers['h'] = 0x21
    memory.registers['a'] = 2
    memory.registers['b'] = 3
    memory.write_memory(0x0000, 0b01101111, restricted=False)  # MOV L, A
    memory.write_memory(0x0001, 0b01110000, restricted=False)  # MOV M, B
    memory.write_memory(0x0002, 0b01110110, restricted=False)  # MOV M, M (HALT)
    cpu.boot(0x0000)
    assert memory.registers['l'] == 2
    assert memory.read_memory(0x2102) == 3


def test_nop():  # Including this for completeness, and for eventual timing tests.
    memory.reset_ram()
    old_registers = memory.registers
    memory.write_memory(0x0001, 0b01110110, restricted=False)
    old_memory = memory.ram
    cpu.boot(0x0000)
    assert memory.ram == old_memory
    assert old_registers == memory.registers


def test_jumps():
    memory.reset_ram()
    memory.write_memory(0x0000, 0b11000011)
    memory.write_memory(0x0001, 0x02)
    memory.write_memory(0x0002, 0x21)
    memory.write_memory(0x0221, 0b01110110)
    memory.write_memory(0x0222, 0b01110110)
    memory.write_memory(0x2102, 0b01110110)
    memory.write_memory(0x2103, 0b01110110)
    memory.write_memory(0x0003, 0b01110110)
    cpu.boot(0x0000)
    assert memory.registers['pc'] == 0x2103  # Not $2102 because PC is incremented after each instruction, like HALT
    memory.reset_ram()
    memory.registers['zero'] = 1
    memory.write_memory(0x0000, 0b11000010)
    memory.write_memory(0x0001, 0x02)
    memory.write_memory(0x0002, 0x21)
    memory.write_memory(0x0003, 0b01110110)
    memory.write_memory(0x2102, 0b01110110)
    cpu.boot(0x0000)
    assert memory.registers['pc'] == 0x0004
    memory.registers['zero'] = 0
    cpu.boot(0x0000)
    assert memory.registers['pc'] == 0x2103
