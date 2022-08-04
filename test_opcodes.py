import cpu
import memory

HALT = 0b01110110


def test_mov():
    memory.reset_ram()
    memory.registers['h'] = 0x21
    memory.registers['a'] = 2
    memory.registers['b'] = 3
    memory.write_memory(0x0000, 0b01101111, restricted=False)  # MOV L, A
    memory.write_memory(0x0001, 0b01110000, restricted=False)  # MOV M, B
    memory.write_memory(0x0002, 0x7E, restricted=False)        # MOV A, M
    memory.write_memory(0x0003, HALT, restricted=False)  # MOV M, M (HALT)
    cpu.boot(0x0000)
    assert memory.registers['l'] == 2
    assert memory.read_memory(0x2102) == 3
    assert memory.registers['a'] == 3


def test_nop():  # Including this for completeness, and for eventual timing tests.
    memory.reset_ram()
    old_registers = memory.registers
    memory.write_memory(0x0001, HALT, restricted=False)
    old_memory = memory.ram
    cpu.boot(0x0000)
    assert memory.ram == old_memory
    assert old_registers == memory.registers


def test_jumps():
    memory.reset_ram()
    memory.write_memory(0x0000, 0b11000011, restricted=False)
    memory.write_memory(0x0001, 0x02, restricted=False)
    memory.write_memory(0x0002, 0x21, restricted=False)
    memory.write_memory(0x0221, HALT, restricted=False)
    memory.write_memory(0x0222, HALT, restricted=False)
    memory.write_memory(0x2102, HALT, restricted=False)
    memory.write_memory(0x2103, HALT, restricted=False)
    memory.write_memory(0x0003, HALT, restricted=False)
    cpu.boot(0x0000)
    assert memory.registers['pc'] == 0x2103  # Not $2102 because PC is incremented after each instruction, like HALT
    memory.reset_ram()
    memory.registers['zero'] = 1
    memory.write_memory(0x0000, 0b11000010, restricted=False)
    memory.write_memory(0x0001, 0x02, restricted=False)
    memory.write_memory(0x0002, 0x21, restricted=False)
    memory.write_memory(0x0003, HALT, restricted=False)
    memory.write_memory(0x2102, HALT, restricted=False)
    cpu.boot(0x0000)
    assert memory.registers['pc'] == 0x0004
    memory.registers['zero'] = 0
    cpu.boot(0x0000)
    assert memory.registers['pc'] == 0x2103


def test_lxi():
    memory.reset_ram()
    memory.write_memory(0x0000, 0x01, restricted=False)  # LXI B, $2102
    memory.write_memory(0x0001, 0x02, restricted=False)
    memory.write_memory(0x0002, 0x21, restricted=False)
    memory.write_memory(0x0003, HALT, restricted=False)
    cpu.boot(0x0000)
    assert memory.registers['b'] == 0x21
    assert memory.registers['c'] == 0x02
    memory.write_memory(0x0000, 0x31, restricted=False)  # LXI SP, $2102
    cpu.boot(0x0000)
    assert memory.registers['sp'] == 0x2102


def test_mvi():
    memory.reset_ram()
    memory.write_memory(0x0000, 0x06, restricted=False)
    memory.write_memory(0x0001, 0x32, restricted=False)
    memory.write_memory(0x0002, HALT, restricted=False)
    cpu.boot(0x0000)
    assert memory.registers['b'] == 0x32
    memory.registers['h'] = 0x21
    memory.registers['l'] = 0x02
    memory.write_memory(0x0000, 0x36, restricted=False)
    cpu.boot(0x0000)
    assert memory.read_memory(0x2102) == 0x32


def test_call_ret():
    memory.reset_ram()
    memory.registers['sp'] = 0x2300
    memory.registers['c'] = 0x38
    memory.write_memory(0x0000, 0xCD, restricted=False)
    memory.write_memory(0x0001, 0x23, restricted=False)
    memory.write_memory(0x0002, 0x01, restricted=False)
    memory.write_memory(0x0123, 0xC8, restricted=False)
    memory.write_memory(0x0124, 0x51, restricted=False)
    memory.write_memory(0x0125, 0xC9, restricted=False)
    memory.write_memory(0x0003, 0x41, restricted=False)
    memory.write_memory(0x0004, HALT, restricted=False)
    cpu.boot(0x0000)
    assert memory.registers['c'] == 0x38
    assert memory.registers['b'] == 0x38
    assert memory.registers['d'] == 0x38
    memory.registers['zero'] = 1
    memory.registers['b'] = 0
    memory.registers['d'] = 0
    cpu.boot(0x0000)
    assert memory.registers['b'] == 0x38
    assert memory.registers['d'] == 0x00


def test_dcx():
    memory.reset_ram()
    memory.registers['h'] = 0x98
    memory.registers['l'] = 0x00
    memory.write_memory(0x0000, 0x2b, restricted=False)
    memory.write_memory(0x0001, HALT, restricted=False)
    cpu.boot(0x0000)
    assert memory.registers['h'] == 0x97
    assert memory.registers['l'] == 0xFF


def test_ldax():
    memory.reset_ram()
    memory.registers['b'] = 0x21
    memory.registers['c'] = 0x02
    memory.registers['d'] = 0x21
    memory.registers['e'] = 0x03
    memory.write_memory(0x0000, 0x0A, restricted=False)
    memory.write_memory(0x0001, 0x67, restricted=False)
    memory.write_memory(0x0002, 0x1A, restricted=False)
    memory.write_memory(0x0003, HALT, restricted=False)
    memory.write_memory(0x2102, 0xBE, restricted=False)
    memory.write_memory(0x2103, 0xEF, restricted=False)
    cpu.boot(0x0000)
    assert memory.registers['h'] == 0xBE
    assert memory.registers['a'] == 0xEF


def test_inx():
    memory.reset_ram()
    memory.registers['d'] = 0x38
    memory.registers['e'] = 0xFF
    memory.write_memory(0x0000, 0x13, restricted=False)
    memory.write_memory(0x0001, HALT, restricted=False)
    cpu.boot(0x0000)
    assert memory.registers['d'] == 0x39
    assert memory.registers['e'] == 0xFF
    memory.registers['sp'] = 0xFFFF
    memory.write_memory(0x0000, 0x33, restricted=False)
    cpu.boot(0x0000)
    assert memory.registers['sp'] == 0x0000


def test_dcr():
    memory.reset_ram()
    memory.write_memory(0x0000, 0x05, restricted=False)
    memory.write_memory(0x0001, HALT, restricted=False)
    cpu.boot(0x0000)
    assert memory.registers['b'] == 0xFF
    assert memory.registers['sign'] == 1
    assert memory.registers['zero'] == 0
    memory.reset_ram()  # To ensure flags are correct
    memory.registers['h'] = 0x21
    memory.registers['l'] = 0x02
    memory.write_memory(0x0000, 0x35, restricted=False)
    memory.write_memory(0x0001, HALT, restricted=False)
    cpu.boot(0x0000)
    assert memory.registers['h'] == 0x21
    assert memory.registers['l'] == 0x02
    assert memory.read_memory(0x2102) == 0xFF
