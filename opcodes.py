import inout
import memory

cpm_mode = False

pop_push_count = 0

register_pairings = {
    'b': 'c',
    'd': 'e',
    'h': 'l',
}


def nop():
    pass


def jmp():
    lxi('pc')
    memory.registers['pc'] -= 1


def lxi(register):
    if register == 'pc' or register == 'sp':
        memory.registers['pc'] += 1
        byte_a = memory.read_memory(memory.registers['pc'])
        memory.registers['pc'] += 1
        byte_b = memory.read_memory(memory.registers['pc'])
        final_address = (byte_b << 8) + byte_a
        if cpm_mode:  # pragma: no cover
            if final_address == 0:
                print("\n[CP/M] Program returned to CP/M")
                exit()
        memory.registers[register] = final_address
    else:
        pair = register_pairings[register]
        memory.registers['pc'] += 1
        byte_a = memory.read_memory(memory.registers['pc'])
        memory.registers['pc'] += 1
        byte_b = memory.read_memory(memory.registers['pc'])
        memory.registers[register] = byte_b
        memory.registers[pair] = byte_a


def mvi(register):
    memory.registers['pc'] += 1
    byte = memory.read_memory(memory.registers['pc'])
    if register == 'm':
        memory.write_memory((memory.registers['h'] << 8) + memory.registers['l'], byte)
    else:
        memory.registers[register] = byte


def push(data):
    byte_a = data & 0x00FF
    byte_b = (data & 0xFF00) >> 8
    dcx('sp')
    memory.write_memory(memory.registers['sp'], byte_b)
    dcx('sp')
    memory.write_memory(memory.registers['sp'], byte_a)


def pop():
    byte_a = memory.read_memory(memory.registers['sp'])
    memory.registers['sp'] += 1
    byte_b = memory.read_memory(memory.registers['sp'])
    memory.registers['sp'] += 1
    return (byte_b << 8) + byte_a


def push_reg(register):
    if register == 'psw':
        # Generate flag register
        sign = memory.registers['sign']
        zero = memory.registers['zero']
        parity = memory.registers['parity']
        carry = memory.registers['carry']
        aux = memory.registers['aux']
        flag = 0
        flag += sign << 7
        flag += zero << 6
        flag += aux << 4
        flag += parity << 2
        flag += 0b10
        flag += carry
        # Generate PSW
        psw = (memory.registers['a'] << 8) + flag
        # Push it onto the stack
        push(psw)
    else:
        pair = register_pairings[register]
        push((memory.registers[register] << 8) + memory.registers[pair])


def pop_reg(register):
    if register == 'psw':
        # Pop PSW
        value = pop()
        # Set accumulator
        memory.registers['a'] = value >> 8
        # Set flags
        flag = value & 0x00FF
        memory.registers['sign'] = (flag & 0b10000000) >> 7
        memory.registers['zero'] = (flag & 0b01000000) >> 6
        memory.registers['aux'] = (flag & 0b00010000) >> 4
        memory.registers['parity'] = (flag & 0b00000100) >> 2
        memory.registers['carry'] = flag & 0b00000001
    else:
        pair = register_pairings[register]
        value = pop()
        memory.registers[register] = value >> 8
        memory.registers[pair] = value & 0x00FF


def call():
    memory.registers['pc'] += 1
    byte_a = memory.read_memory(memory.registers['pc'])
    memory.registers['pc'] += 1
    byte_b = memory.read_memory(memory.registers['pc'])
    final_address = (byte_b << 8) + byte_a
    if cpm_mode:  # pragma: no cover
        if final_address == 0x0005:
            if memory.registers['c'] == 9:
                msg_address = (memory.registers['d'] << 8) + memory.registers['e']
                current_char = 'begin'
                print("[CP/M BDOS MSG] ", end='')
                while current_char != '$':
                    current_char = chr(memory.read_memory(msg_address))
                    if current_char not in ['\x0c', '\x0d', '\x0a']:
                        print(current_char, end='')
                    msg_address += 1
            elif memory.registers['c'] == 2:
                print(chr(memory.registers['e']), end='')
            else:
                print(f"\n[CP/M BDOS ERR] Unknown call {memory.registers['c']}")
        else:
            push(memory.registers['pc'] + 1)
            memory.registers['pc'] = final_address - 1
    else:
        push(memory.registers['pc'] + 1)
        memory.registers['pc'] = final_address - 1


def dcx(register):
    if register == 'sp':
        memory.registers['sp'] -= 1
        if memory.registers['sp'] < 0x0000:
            memory.registers['sp'] = 0xFFFF
    else:
        pair = register_pairings[register]
        memory.registers[pair] -= 1
        if memory.registers[pair] < 0x00:
            memory.registers[pair] = 0xFF
            memory.registers[register] -= 1
            if memory.registers[register] < 0x00:
                memory.registers[register] = 0xFF


def ldax(register):
    pair = register_pairings[register]
    memory.registers['a'] = memory.read_memory((memory.registers[register] << 8) + memory.registers[pair])


def mov(register_a, register_b):
    if register_a == 'm':
        memory.write_memory((memory.registers['h'] << 8) + memory.registers['l'], memory.registers[register_b])
    else:
        if register_b == 'm':
            memory.registers[register_a] = memory.read_memory((memory.registers['h'] << 8) + memory.registers['l'])
        else:
            memory.registers[register_a] = memory.registers[register_b]


def inx(register):
    if register == 'sp':
        memory.registers['sp'] += 1
        if memory.registers['sp'] > 0xFFFF:
            memory.registers['sp'] = 0x0000
    else:
        pair = register_pairings[register]
        memory.registers[pair] += 1
        if memory.registers[pair] > 0xFF:
            memory.registers[pair] = 0x00
            memory.registers[register] += 1
            if memory.registers[register] > 0xFF:
                memory.registers[register] = 0x00


def dcr(register):
    if register == 'm':
        address = (memory.registers['h'] << 8) + memory.registers['l']
        value = memory.read_memory(address)
        value -= 1
        if value == 0x00:
            memory.registers['zero'] = 1
        else:
            memory.registers['zero'] = 0
        if value < 0x00:
            value = 0xFF
        memory.write_memory(address, value)
        ones = bin(value).count('1')
        if ones / 2 == round(ones / 2):
            memory.registers['parity'] = 1
        else:
            memory.registers['parity'] = 0
        if value > 0b01111111:
            memory.registers['sign'] = 1
        else:
            memory.registers['sign'] = 0
    else:
        memory.registers[register] -= 1
        if memory.registers[register] == 0x00:
            memory.registers['zero'] = 1
        else:
            memory.registers['zero'] = 0
        if memory.registers[register] < 0x00:
            memory.registers[register] = 0xFF
        ones = bin(memory.registers[register]).count('1')
        if ones / 2 == round(ones / 2):
            memory.registers['parity'] = 1
        else:
            memory.registers['parity'] = 0
        if memory.registers[register] > 0b01111111:
            memory.registers['sign'] = 1
        else:
            memory.registers['sign'] = 0


def inr(register):
    if register == 'm':
        address = (memory.registers['h'] << 8) + memory.registers['l']
        value = memory.read_memory(address)
        value += 1
        if value == 0x00:
            memory.registers['zero'] = 1
        else:
            memory.registers['zero'] = 0
        if value > 0xFF:
            value = 0x00
        memory.write_memory(address, value)
        ones = bin(value).count('1')
        if ones / 2 == round(ones / 2):
            memory.registers['parity'] = 1
        else:
            memory.registers['parity'] = 0
        if value > 0b01111111:
            memory.registers['sign'] = 1
        else:
            memory.registers['sign'] = 0
    else:
        memory.registers[register] += 1
        if memory.registers[register] == 0x00:
            memory.registers['zero'] = 1
        else:
            memory.registers['zero'] = 0
        if memory.registers[register] > 0xFF:
            memory.registers[register] = 0x00
        ones = bin(memory.registers[register]).count('1')
        if ones / 2 == round(ones / 2):
            memory.registers['parity'] = 1
        else:
            memory.registers['parity'] = 0
        if memory.registers[register] > 0b01111111:
            memory.registers['sign'] = 1
        else:
            memory.registers['sign'] = 0


def jnz():
    if memory.registers['zero'] == 0:
        jmp()
    else:
        memory.registers['pc'] += 2


def jz():
    if memory.registers['zero'] == 1:
        jmp()
    else:
        memory.registers['pc'] += 2


def jc():
    if memory.registers['carry'] == 1:
        jmp()
    else:
        memory.registers['pc'] += 2


def jnc():
    if memory.registers['carry'] == 0:
        jmp()
    else:
        memory.registers['pc'] += 2


def ret():
    memory.registers['pc'] = pop() - 1


def rz():
    if memory.registers['zero'] == 1:
        ret()


def cpi():
    memory.registers['pc'] += 1
    compare_from = memory.registers['a']
    compare_to = memory.read_memory(memory.registers['pc'])
    # Turn compare_to into a negative number, and then unsign it.
    old_compare_to = compare_to
    compare_to = memory.unsign(0 - memory.sign(compare_to))
    virtual_a = compare_from + compare_to
    if virtual_a > 255:
        virtual_a -= 256
    if compare_from < old_compare_to:
        memory.registers['carry'] = 1
    else:
        memory.registers['carry'] = 0
    if virtual_a > 127:
        memory.registers['sign'] = 1
    else:
        memory.registers['sign'] = 0
    if virtual_a == 0:
        memory.registers['zero'] = 1
    else:
        memory.registers['zero'] = 0
    ones = bin(virtual_a).count('1')
    if ones / 2 == round(ones / 2):
        memory.registers['parity'] = 1
    else:
        memory.registers['parity'] = 0


def sui():
    memory.registers['pc'] += 1
    compare_from = memory.registers['a']
    compare_to = memory.read_memory(memory.registers['pc'])
    # Turn compare_to into a negative number, and then unsign it.
    compare_to = memory.unsign(0 - memory.sign(compare_to))
    virtual_a = compare_from + compare_to
    if virtual_a > 255:
        virtual_a -= 256
        memory.registers['carry'] = 0
    else:
        memory.registers['carry'] = 1
    if virtual_a > 127:
        memory.registers['sign'] = 1
    else:
        memory.registers['sign'] = 0
    if virtual_a == 0:
        memory.registers['zero'] = 1
    else:
        memory.registers['zero'] = 0
    ones = bin(virtual_a).count('1')
    if ones / 2 == round(ones / 2):
        memory.registers['parity'] = 1
    else:
        memory.registers['parity'] = 0
    memory.registers['a'] = virtual_a


def dad(register):
    hl = (memory.registers['h'] << 8) + memory.registers['l']
    if register == 'sp':
        to_add = memory.registers['sp']
    else:
        pair = register_pairings[register]
        to_add = (memory.registers[register] << 8) + memory.registers[pair]
    total = hl + to_add
    if total > 0xFFFF:
        total -= 0x10000
        memory.registers['carry'] = 1
    else:
        memory.registers['carry'] = 0
    memory.registers['l'] = total & 0x00FF
    memory.registers['h'] = total >> 8


def xchg():
    swap = memory.registers['d']
    memory.registers['d'] = memory.registers['h']
    memory.registers['h'] = swap
    swap = memory.registers['e']
    memory.registers['e'] = memory.registers['l']
    memory.registers['l'] = swap


def out():
    memory.registers['pc'] += 1
    inout.out(memory.read_memory(memory.registers['pc']))


def inp():
    memory.registers['pc'] += 1
    inout.inp(memory.read_memory(memory.registers['pc']))


def rrc():
    # carry is last bit of accumulator
    bits = bin(memory.registers['a'])[2:]
    while len(bits) < 8:
        bits = '0' + bits
    memory.registers['carry'] = int(bits[::-1][0])
    memory.registers['a'] >>= 1
    memory.registers['a'] += memory.registers['carry'] << 7


def rlc():
    bits = bin(memory.registers['a'])[2:]
    while len(bits) < 8:
        bits = '0' + bits
    memory.registers['carry'] = int(bits[0])
    memory.registers['a'] <<= 1
    memory.registers['a'] %= 256
    memory.registers['a'] += memory.registers['carry']


def ani():
    memory.registers['pc'] += 1
    to_and = memory.read_memory(memory.registers['pc'])
    result = memory.registers['a'] & to_and
    if result == 0x00:
        memory.registers['zero'] = 1
    else:
        memory.registers['zero'] = 0
    if result > 0b01111111:
        memory.registers['sign'] = 1
    else:
        memory.registers['sign'] = 0
    ones = bin(result).count('1')
    if ones / 2 == round(ones / 2):
        memory.registers['parity'] = 1
    else:
        memory.registers['parity'] = 0
    memory.registers['carry'] = 0  # I don't think this can ever be set. I might be wrong, though.
    memory.registers['a'] = result


def adi():
    memory.registers['pc'] += 1
    to_add = memory.read_memory(memory.registers['pc'])
    a = memory.registers['a']
    result = a + to_add
    if result > 0xFF:
        result -= 0x100
        memory.registers['carry'] = 1
    else:
        memory.registers['carry'] = 0
    if result == 0:
        memory.registers['zero'] = 1
    else:
        memory.registers['zero'] = 0
    if result > 0b01111111:
        memory.registers['sign'] = 1
    else:
        memory.registers['sign'] = 0
    ones = bin(result).count('1')
    if ones / 2 == round(ones / 2):
        memory.registers['parity'] = 1
    else:
        memory.registers['parity'] = 0
    memory.registers['a'] = result


def lda():
    memory.registers['pc'] += 1
    low = memory.read_memory(memory.registers['pc'])
    memory.registers['pc'] += 1
    high = memory.read_memory(memory.registers['pc'])
    address = (high << 8) + low
    memory.registers['a'] = memory.read_memory(address)


def sta():
    memory.registers['pc'] += 1
    low = memory.read_memory(memory.registers['pc'])
    memory.registers['pc'] += 1
    high = memory.read_memory(memory.registers['pc'])
    address = (high << 8) + low
    memory.write_memory(address, memory.registers['a'])


def xra(reg):
    if reg == 'm':
        address = (memory.registers['h'] << 8) + memory.registers['l']
        value = memory.read_memory(address)
    else:
        value = memory.registers[reg]
    a = memory.registers['a']
    a ^= value
    if a == 0x00:
        memory.registers['zero'] = 1
    else:
        memory.registers['zero'] = 0
    memory.registers['sign'] = a >> 7
    ones = bin(a).count('1')
    if ones / 2 == round(ones / 2):
        memory.registers['parity'] = 1
    else:
        memory.registers['parity'] = 0
    memory.registers['carry'] = 0
    memory.registers['a'] = a


def ora(reg):
    if reg == 'm':
        address = (memory.registers['h'] << 8) + memory.registers['l']
        value = memory.read_memory(address)
    else:
        value = memory.registers[reg]
    a = memory.registers['a']
    a |= value
    if a == 0x00:
        memory.registers['zero'] = 1
    else:
        memory.registers['zero'] = 0
    memory.registers['sign'] = a >> 7
    ones = bin(a).count('1')
    if ones / 2 == round(ones / 2):
        memory.registers['parity'] = 1
    else:
        memory.registers['parity'] = 0
    memory.registers['carry'] = 0
    memory.registers['aux'] = 0
    memory.registers['a'] = a


def xri():
    memory.registers['pc'] += 1
    value = memory.read_memory(memory.registers['pc'])
    a = memory.registers['a']
    a ^= value
    if a == 0x00:
        memory.registers['zero'] = 1
    else:
        memory.registers['zero'] = 0
    memory.registers['sign'] = a >> 7
    ones = bin(a).count('1')
    if ones / 2 == round(ones / 2):
        memory.registers['parity'] = 1
    else:
        memory.registers['parity'] = 0
    memory.registers['carry'] = 0
    memory.registers['a'] = a


def ei():
    # print("Interrupts enabled")
    memory.registers['interrupts'] = 1


def di():
    # print("Interrupts disabled")
    memory.registers['interrupts'] = 0


def rst(value):
    # print(f"RST {value} @ pc {hex(memory.registers['pc'])}")
    push(memory.registers['pc'])
    memory.registers['pc'] = (value * 8) - 1


def ana(register):
    if register == 'm':
        address = (memory.registers['h'] << 8) + memory.registers['l']
        value = memory.read_memory(address)
    else:
        value = memory.registers[register]
    a = memory.registers['a']
    a &= value
    if a == 0x00:
        memory.registers['zero'] = 1
    else:
        memory.registers['zero'] = 0
    memory.registers['sign'] = a >> 7
    ones = bin(a).count('1')
    if ones / 2 == round(ones / 2):
        memory.registers['parity'] = 1
    else:
        memory.registers['parity'] = 0
    memory.registers['carry'] = 0
    memory.registers['a'] = a


def xthl():
    new_hl = pop()
    push((memory.registers['h'] << 8) + memory.registers['l'])
    memory.registers['h'] = new_hl >> 8
    memory.registers['l'] = new_hl & 0x00FF


def pchl():
    address = (memory.registers['h'] << 8) + memory.registers['l']
    memory.registers['pc'] = address - 1


def rnz():
    if memory.registers['zero'] == 0:
        ret()
    else:
        nop()


def rnc():
    if memory.registers['carry'] == 0:
        ret()
    else:
        nop()


def stc():
    memory.registers['carry'] = 1


def lhld():
    memory.registers['pc'] += 1
    low = memory.read_memory(memory.registers['pc'])
    memory.registers['pc'] += 1
    high = memory.read_memory(memory.registers['pc'])
    address = (high << 8) + low
    memory.registers['l'] = memory.read_memory(address)
    memory.registers['h'] = memory.read_memory(address + 1)


def shld():
    memory.registers['pc'] += 1
    low = memory.read_memory(memory.registers['pc'])
    memory.registers['pc'] += 1
    high = memory.read_memory(memory.registers['pc'])
    address = (high << 8) + low
    memory.write_memory(address, memory.registers['l'])
    memory.write_memory(address + 1, memory.registers['h'])


def rc():
    if memory.registers['carry'] == 1:
        ret()
    else:
        nop()


def jm():
    if memory.registers['sign'] == 1:
        jmp()
    else:
        memory.registers['pc'] += 2


def jpe():
    if memory.registers['parity'] == 1:
        jmp()
    else:
        memory.registers['pc'] += 2


def jp():
    if memory.registers['sign'] == 0:
        jmp()
    else:
        memory.registers['pc'] += 2


def jpo():
    if memory.registers['parity'] == 0:
        jmp()
    else:
        memory.registers['pc'] += 2


def aci():
    memory.registers['a'] += memory.registers['carry']
    memory.registers['pc'] += 1
    to_add = memory.read_memory(memory.registers['pc'])
    a = memory.registers['a']
    result = a + to_add
    if result > 0xFF:
        result -= 0x100
        memory.registers['carry'] = 1
    else:
        memory.registers['carry'] = 0
    if result == 0:
        memory.registers['zero'] = 1
    else:
        memory.registers['zero'] = 0
    if result > 0b01111111:
        memory.registers['sign'] = 1
    else:
        memory.registers['sign'] = 0
    ones = bin(result).count('1')
    if ones / 2 == round(ones / 2):
        memory.registers['parity'] = 1
    else:
        memory.registers['parity'] = 0
    memory.registers['a'] = result


def sbi():
    memory.registers['pc'] += 1
    compare_from = memory.registers['a']
    compare_to = memory.read_memory(memory.registers['pc'])
    compare_to += memory.registers['carry']
    # Turn compare_to into a negative number, and then unsign it.
    compare_to = memory.unsign(0 - memory.sign(compare_to))
    virtual_a = compare_from + compare_to
    if virtual_a > 255:
        virtual_a -= 256
        memory.registers['carry'] = 0
    else:
        memory.registers['carry'] = 1
    if virtual_a > 127:
        memory.registers['sign'] = 1
    else:
        memory.registers['sign'] = 0
    if virtual_a == 0:
        memory.registers['zero'] = 1
    else:
        memory.registers['zero'] = 0
    ones = bin(virtual_a).count('1')
    if ones / 2 == round(ones / 2):
        memory.registers['parity'] = 1
    else:
        memory.registers['parity'] = 0
    memory.registers['a'] = virtual_a


def ori():
    memory.registers['pc'] += 1
    to_and = memory.read_memory(memory.registers['pc'])
    result = memory.registers['a'] | to_and
    if result == 0x00:
        memory.registers['zero'] = 1
    else:
        memory.registers['zero'] = 0
    if result > 0b01111111:
        memory.registers['sign'] = 1
    else:
        memory.registers['sign'] = 0
    ones = bin(result).count('1')
    if ones / 2 == round(ones / 2):
        memory.registers['parity'] = 1
    else:
        memory.registers['parity'] = 0
    memory.registers['carry'] = 0  # I don't think this can ever be set. I might be wrong, though.
    memory.registers['a'] = result


def cc():
    if memory.registers['carry']:
        call()
    else:
        memory.registers['pc'] += 2


def adc(reg):
    if reg == 'm':
        to_add = memory.read_memory((memory.registers['h'] << 8) + memory.registers['l'])
    else:
        to_add = memory.registers[reg]
    a = memory.registers['a']
    result = a + to_add + memory.registers['carry']
    if result > 0xFF:
        result -= 0x100
        memory.registers['carry'] = 1
    else:
        memory.registers['carry'] = 0
    if result == 0:
        memory.registers['zero'] = 1
    else:
        memory.registers['zero'] = 0
    if result > 0b01111111:
        memory.registers['sign'] = 1
    else:
        memory.registers['sign'] = 0
    ones = bin(result).count('1')
    if ones / 2 == round(ones / 2):
        memory.registers['parity'] = 1
    else:
        memory.registers['parity'] = 0
    memory.registers['a'] = result


def cnc():
    if not memory.registers['carry']:
        call()
    else:
        memory.registers['pc'] += 2


def cpo():
    if not memory.registers['parity']:
        call()
    else:
        memory.registers['pc'] += 2


def cm():
    if memory.registers['sign']:
        call()
    else:
        memory.registers['pc'] += 2


def cnz():
    if not memory.registers['zero']:
        call()
    else:
        memory.registers['pc'] += 2


def cpe():
    if memory.registers['parity']:
        call()
    else:
        memory.registers['pc'] += 2


def cp():
    if not memory.registers['sign']:
        call()
    else:
        memory.registers['pc'] += 2


def cz():
    if memory.registers['zero']:
        call()
    else:
        memory.registers['pc'] += 2


def rpe():
    if memory.registers['parity']:
        ret()


def rpo():
    if not memory.registers['parity']:
        ret()


def rm():
    if memory.registers['sign']:
        ret()


def rp():
    if not memory.registers['sign']:
        ret()


def add(reg):
    if reg == 'm':
        to_add = memory.read_memory((memory.registers['h'] << 8) + memory.registers['l'])
    else:
        to_add = memory.registers[reg]
    a = memory.registers['a']
    result = a + to_add
    if (a & 0x0F) + (to_add & 0x0F) > 0x0F:
        memory.registers['aux'] = 1
    else:
        memory.registers['aux'] = 0
    if result > 0xFF:
        result -= 0x100
        memory.registers['carry'] = 1
    else:
        memory.registers['carry'] = 0
    if result == 0:
        memory.registers['zero'] = 1
    else:
        memory.registers['zero'] = 0
    if result > 0b01111111:
        memory.registers['sign'] = 1
    else:
        memory.registers['sign'] = 0
    ones = bin(result).count('1')
    if ones / 2 == round(ones / 2):
        memory.registers['parity'] = 1
    else:
        memory.registers['parity'] = 0
    memory.registers['a'] = result


def sub(reg):
    if reg == 'm':
        compare_to = memory.read_memory((memory.registers['h'] << 8) + memory.registers['l'])
    else:
        compare_to = memory.registers[reg]
    compare_from = memory.registers['a']
    # Turn compare_to into a negative number, and then unsign it.
    compare_to = memory.unsign(0 - memory.sign(compare_to))
    virtual_a = compare_from + compare_to
    if virtual_a > 255:
        virtual_a -= 256
        memory.registers['carry'] = 0
    else:
        memory.registers['carry'] = 1
    if virtual_a > 127:
        memory.registers['sign'] = 1
    else:
        memory.registers['sign'] = 0
    if virtual_a == 0:
        memory.registers['zero'] = 1
    else:
        memory.registers['zero'] = 0
    ones = bin(virtual_a).count('1')
    if ones / 2 == round(ones / 2):
        memory.registers['parity'] = 1
    else:
        memory.registers['parity'] = 0
    memory.registers['a'] = virtual_a


def sbb(reg):
    if reg == 'm':
        compare_to = memory.read_memory((memory.registers['h'] << 8) + memory.registers['l'])
    else:
        compare_to = memory.registers[reg]
    compare_to += memory.registers['carry']
    compare_from = memory.registers['a']
    # Turn compare_to into a negative number, and then unsign it.
    compare_to = memory.unsign(0 - memory.sign(compare_to))
    virtual_a = compare_from + compare_to
    if virtual_a > 255:
        virtual_a -= 256
        memory.registers['carry'] = 0
    else:
        memory.registers['carry'] = 1
    if virtual_a > 127:
        memory.registers['sign'] = 1
    else:
        memory.registers['sign'] = 0
    if virtual_a == 0:
        memory.registers['zero'] = 1
    else:
        memory.registers['zero'] = 0
    ones = bin(virtual_a).count('1')
    if ones / 2 == round(ones / 2):
        memory.registers['parity'] = 1
    else:
        memory.registers['parity'] = 0
    memory.registers['a'] = virtual_a


def cmp(reg):
    if reg == 'm':
        compare_to = memory.read_memory((memory.registers['h'] << 8) + memory.registers['l'])
    else:
        compare_to = memory.registers[reg]
    compare_from = memory.registers['a']
    # Turn compare_to into a negative number, and then unsign it.
    compare_to = memory.unsign(0 - memory.sign(compare_to))
    virtual_a = compare_from + compare_to
    if virtual_a > 255:
        virtual_a -= 256
        memory.registers['carry'] = 0
    else:
        memory.registers['carry'] = 1
    if virtual_a > 127:
        memory.registers['sign'] = 1
    else:
        memory.registers['sign'] = 0
    if virtual_a == 0:
        memory.registers['zero'] = 1
    else:
        memory.registers['zero'] = 0
    ones = bin(virtual_a).count('1')
    if ones / 2 == round(ones / 2):
        memory.registers['parity'] = 1
    else:
        memory.registers['parity'] = 0


def stax(register):
    pair = register_pairings[register]
    memory.write_memory((memory.registers[register] << 8) + memory.registers[pair], memory.registers['a'])


def cmc():
    if memory.registers['carry']:
        memory.registers['carry'] = 0
    else:
        memory.registers['carry'] = 1


def cma():
    memory.registers['a'] ^= 0xFF


def ral():
    bits = bin(memory.registers['a'])[2:]
    while len(bits) < 8:
        bits = '0' + bits
    swap_carry = memory.registers['carry']
    memory.registers['carry'] = int(bits[0])
    memory.registers['a'] <<= 1
    memory.registers['a'] %= 256
    memory.registers['a'] += swap_carry


def rar():
    # carry is last bit of accumulator
    bits = bin(memory.registers['a'])[2:]
    while len(bits) < 8:
        bits = '0' + bits
    swap_carry = memory.registers['carry']
    memory.registers['carry'] = int(bits[::-1][0])
    memory.registers['a'] >>= 1
    memory.registers['a'] += swap_carry << 7


def sphl():
    address = (memory.registers['h'] << 8) + memory.registers['l']
    memory.registers['sp'] = address


def daa():  # Incredibly scuffed because no AC implementation
    a = memory.registers['a']
    if a & 0x0f > 9 or memory.registers['aux']:
        if a & 0x0f + 6 > 0x0f:
            memory.registers['aux'] = 1
        else:
            memory.registers['aux'] = 0
        a += 6
    if a >> 4 > 9 or memory.registers['carry']:
        a += 0x60
    if a > 0xff:
        a -= 0x100
        memory.registers['carry'] = 1
    memory.registers['a'] = a
    # The carry bit is not reset.
