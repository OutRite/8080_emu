import memory

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
    memory.write_memory(memory.registers['sp'], byte_b)
    memory.registers['sp'] -= 1
    memory.write_memory(memory.registers['sp'], byte_a)
    memory.registers['sp'] -= 1


def pop():
    memory.registers['sp'] += 1
    byte_a = memory.read_memory(memory.registers['sp'])
    memory.write_memory(memory.registers['sp'], 0x00)
    memory.registers['sp'] += 1
    byte_b = memory.read_memory(memory.registers['sp'])
    memory.write_memory(memory.registers['sp'], 0x00)
    return (byte_b << 8) + byte_a


def push_reg(register):
    if register == 'psw':
        raise ValueError("uh oh, PSW moment")
    else:
        pair = register_pairings[register]
    push((memory.registers[register] << 8) + memory.registers[pair])


def call():
    memory.registers['pc'] += 1
    byte_a = memory.read_memory(memory.registers['pc'])
    memory.registers['pc'] += 1
    byte_b = memory.read_memory(memory.registers['pc'])
    final_address = (byte_b << 8) + byte_a
    push(memory.registers['pc'])
    memory.registers['pc'] = final_address-1


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
        if ones/2 == round(ones/2):
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
        if ones/2 == round(ones/2):
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


def ret():
    memory.registers['pc'] = pop()


def rz():
    if memory.registers['zero'] == 1:
        ret()


def inr(register):
    memory.registers[register] -= 1
    if memory.registers[register] > 0xFF:
        memory.registers[register] = 0x00
    if memory.registers[register] == 0x00:
        memory.registers['zero'] = 1
    else:
        memory.registers['zero'] = 0
    ones = bin(memory.registers[register]).count('1')
    if ones/2 == round(ones/2):
        memory.registers['parity'] = 1
    else:
        memory.registers['parity'] = 0
    if memory.registers[register] > 0b01111111:
        memory.registers['sign'] = 1
    else:
        memory.registers['sign'] = 0
