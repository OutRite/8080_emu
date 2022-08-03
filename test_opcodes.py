import cpu
import memory


def test_mov():
    memory.registers['h'] = 0x21
    memory.registers['a'] = 2
    memory.registers['b'] = 3
    memory.write_memory(0x0000, 0b01101111, restricted=False)  # MOV L, A
    memory.write_memory(0x0001, 0b01110000, restricted=False)  # MOV M, B
    memory.write_memory(0x0002, 0b01110110, restricted=False)  # MOV M, M (HALT)
    cpu.boot(0x0000)
    assert memory.registers['l'] == 2
    assert memory.read_memory(0x2102) == 3
