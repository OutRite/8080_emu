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
    memory.registers['h'] = 0x00
    memory.registers['l'] = 0x00
    memory.registers['sp'] = 0x1234
    cpu.boot(0x0000)
    assert memory.registers['h'] == 0xFF
    assert memory.registers['l'] == 0xFF
    memory.write_memory(0x0000, 0x3b, restricted=False)
    cpu.boot(0x0000)
    assert memory.registers['sp'] == 0x1233
    memory.registers['sp'] = 0x0000
    cpu.boot(0x0000)
    assert memory.registers['sp'] == 0xFFFF


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
    assert memory.registers['e'] == 0x00
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


def test_cpi():
    memory.reset_ram()
    memory.registers['a'] = 0x10
    memory.write_memory(0x0000, 0xFE, restricted=False)
    memory.write_memory(0x0001, 0x10, restricted=False)
    memory.write_memory(0x0002, HALT, restricted=False)
    cpu.boot(0x0000)
    assert memory.registers['a'] == 0x10
    assert memory.registers['zero'] == 1
    assert memory.registers['sign'] == 0
    memory.write_memory(0x0001, 0x20, restricted=False)
    cpu.boot(0x0000)
    assert memory.registers['zero'] == 0
    assert memory.registers['sign'] == 1


def test_push_pop():
    memory.reset_ram()
    memory.registers['sp'] = 0x2102
    memory.registers['d'] = 0x00
    memory.registers['e'] = 0x10
    memory.write_memory(0x0000, 0xD5, restricted=False)
    memory.write_memory(0x0001, 0xC9, restricted=False)
    memory.write_memory(0x0002, HALT, restricted=False)
    memory.write_memory(0x0010, HALT, restricted=False)
    memory.write_memory(0x1000, HALT, restricted=False)
    cpu.boot(0x0000)
    assert memory.registers['pc'] == 0x0011
    memory.write_memory(0x0001, 0xE1, restricted=False)
    cpu.boot(0x0000)
    assert memory.registers['h'] == 0x00
    assert memory.registers['l'] == 0x10
    assert memory.registers['sp'] == 0x2102


def test_dad():
    memory.reset_ram()
    memory.registers['b'] = 0x33
    memory.registers['c'] = 0x9F
    memory.registers['h'] = 0xA1
    memory.registers['l'] = 0x7B
    memory.write_memory(0x0000, 0x09, restricted=False)
    memory.write_memory(0x0001, HALT, restricted=False)
    cpu.boot(0x0000)
    assert memory.registers['h'] == 0xD5
    assert memory.registers['l'] == 0x1A
    assert memory.registers['carry'] == 0
    memory.registers['h'] = 0b11111000
    memory.registers['l'] = 0
    memory.write_memory(0x0000, 0x29, restricted=False)
    cpu.boot(0x0000)
    assert memory.registers['h'] == 0b11110000
    assert memory.registers['l'] == 0
    assert memory.registers['carry'] == 1


def test_xchg():
    memory.reset_ram()
    memory.registers['d'] = 0x33
    memory.registers['e'] = 0x55
    memory.registers['h'] = 0x00
    memory.registers['l'] = 0xFF
    memory.write_memory(0x0000, 0xEB, restricted=False)
    memory.write_memory(0x0001, HALT, restricted=False)
    cpu.boot(0x0000)
    assert memory.registers['d'] == 0x00
    assert memory.registers['e'] == 0xFF
    assert memory.registers['h'] == 0x33
    assert memory.registers['l'] == 0x55


def test_sphl():
    memory.reset_ram()
    memory.registers['sp'] = 0x2102
    memory.registers['h'] = 0x20
    memory.registers['l'] = 0x21
    memory.write_memory(0x0000, 0xF9, restricted=False)
    memory.write_memory(0x0001, HALT, restricted=False)
    cpu.boot(0x0000)
    assert memory.registers['sp'] == 0x2021
    assert memory.registers['h'] == 0x20
    assert memory.registers['l'] == 0x21


def test_rrc():
    memory.reset_ram()
    memory.registers['a'] = 0b11110010
    memory.write_memory(0x0000, 0x0F, restricted=False)
    memory.write_memory(0x0001, HALT, restricted=False)
    cpu.boot(0x0000)
    assert memory.registers['a'] == 0b01111001
    assert memory.registers['carry'] == 0


def test_daa():
    memory.reset_ram()
    memory.registers['a'] = 0x9B
    memory.registers['carry'] = 0
    memory.registers['aux'] = 0
    memory.write_memory(0x0000, 0x27, restricted=False)
    memory.write_memory(0x0001, HALT, restricted=False)
    cpu.boot(0x0000)
    assert memory.registers['a'] == 0x01
    assert memory.registers['carry'] == 1
    assert memory.registers['aux'] == 1


def test_ral():
    memory.reset_ram()
    memory.registers['a'] = 0xB5
    memory.registers['carry'] = 0
    memory.write_memory(0x0000, 0b00010111, restricted=False)
    memory.write_memory(0x0001, HALT, restricted=False)
    cpu.boot(0x0000)
    assert memory.registers['a'] == 0x6A
    assert memory.registers['carry'] == 1


def test_rar():
    memory.reset_ram()
    memory.registers['a'] = 0x6A
    memory.registers['carry'] = 1
    memory.write_memory(0x0000, 0b00011111, restricted=False)
    memory.write_memory(0x0001, HALT, restricted=False)
    cpu.boot(0x0000)
    assert memory.registers['a'] == 0xB5
    assert memory.registers['carry'] == 0


def test_cma():
    memory.reset_ram()
    memory.registers['a'] = 0x51
    memory.write_memory(0x0000, 0b00101111, restricted=False)
    memory.write_memory(0x0001, HALT, restricted=False)
    cpu.boot(0x0000)
    assert memory.registers['a'] == 0xAE


def test_cmc():
    memory.reset_ram()
    memory.registers['carry'] = 0
    memory.write_memory(0x0000, 0b00111111, restricted=False)
    memory.write_memory(0x0001, HALT, restricted=False)
    cpu.boot(0x0000)
    assert memory.registers['carry'] == 1
    cpu.boot(0x0000)
    assert memory.registers['carry'] == 0


def test_stax():
    memory.reset_ram()
    memory.registers['b'] = 0x21
    memory.registers['c'] = 0x02
    memory.registers['a'] = 0xBE
    memory.write_memory(0x0000, 0b00000010, restricted=False)
    memory.write_memory(0x0001, HALT, restricted=False)
    cpu.boot(0x0000)
    assert memory.read_memory(0x2102) == 0xBE


def test_cmp():
    memory.reset_ram()
    memory.registers['a'] = 0x0A
    memory.registers['e'] = 0x05
    memory.write_memory(0x0000, 0xBB, restricted=False)
    memory.write_memory(0x0001, HALT, restricted=False)
    cpu.boot(0x0000)
    assert memory.registers['carry'] == 0
    assert memory.registers['zero'] == 0
    memory.registers['a'] = 0x02
    cpu.boot(0x0000)
    assert memory.registers['carry'] == 1
    assert memory.registers['zero'] == 0
    memory.registers['a'] = 0b11100101
    cpu.boot(0x0000)
    assert memory.registers['carry'] == 0
    assert memory.registers['zero'] == 0
