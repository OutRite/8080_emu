import memory
import opcodes

rp = {
    '00': 'b',
    '01': 'd',
    '10': 'h',
    '11': 'sp'
}
reg = {
    '000': 'b',
    '001': 'c',
    '010': 'd',
    '011': 'e',
    '100': 'h',
    '101': 'l',
    '110': 'm',
    '111': 'a'
}

class UnrecognizedOpcode(Exception):
    pass


def boot(address):
    print(f"Booting from address {address}...")
    memory.registers['pc'] = address
    running = True
    while running:
        current_opcode = memory.read_memory(memory.registers['pc'])
        opcode_bin = bin(current_opcode)[2:]
        while len(opcode_bin) < 8:
            opcode_bin = '0' + opcode_bin
        if opcode_bin == '00000000':
            opcodes.nop()
        elif opcode_bin[:2] == '11' and opcode_bin[5:7] == '01':  # JUMP INSTRUCTIONS
            if opcode_bin[2:5] == '000':
                if opcode_bin[7] == '0':
                    opcodes.jnz()
                else:
                    opcodes.jmp()
            else:
                UnrecognizedOpcode(f"Unknown JUMP {opcode_bin[2:5]} opcode: {current_opcode}")
        elif opcode_bin[:2] == '00' and opcode_bin[4:] == '0001':
            opcodes.lxi(rp[opcode_bin[2:4]])
        elif opcode_bin[:2] == '00' and opcode_bin[5:] == '110':
            opcodes.mvi(reg[opcode_bin[2:5]])
        elif opcode_bin == '11001101':
            opcodes.call()
        elif opcode_bin[:2] == '00' and opcode_bin[4:] == '1011':
            opcodes.dcx(rp[opcode_bin[2:4]])
        elif opcode_bin[:3] == '000' and opcode_bin[4:] == '1010':
            if opcode_bin[3] == '0':
                opcodes.ldax('b')
            else:
                opcodes.ldax('d')
        elif opcode_bin[:2] == '01':
            dst = reg[opcode_bin[2:5]]
            src = reg[opcode_bin[5:]]
            if dst == src and dst == 'm':
                running = False
            else:
                opcodes.mov(dst, src)
        elif opcode_bin[:2] == '00' and opcode_bin[4:] == '0011':
            opcodes.inx(rp[opcode_bin[2:4]])
        elif opcode_bin[:2] == '00' and opcode_bin[5:] == '101':
            opcodes.dcr(reg[opcode_bin[2:5]])
        elif opcode_bin[:2] == '11' and opcode_bin[5:7] == '00':
            if opcode_bin[2:5] == '001':
                if opcode_bin[7] == '0':
                    opcodes.rz()
                else:
                    opcodes.ret()
            else:
                UnrecognizedOpcode(f"Unknown RETURN {opcode_bin[2:5]} opcode: {current_opcode}")
        else:
            raise UnrecognizedOpcode(f"Opcode {hex(current_opcode)} not recognized at PC {hex(memory.registers['pc'])}")
        memory.registers['pc'] += 1


def legacy_boot(address):
    print(f"Booting from address {address}...")
    memory.registers['pc'] = address
    running = True
    while running:
        current_opcode = memory.read_memory(memory.registers['pc'])
        if current_opcode == 0x00:
            opcodes.nop()
        elif current_opcode == 0x01:
            opcodes.lxi('b')
        elif current_opcode == 0x03:
            opcodes.inx('b')
        elif current_opcode == 0x04:
            opcodes.inr('b')
        elif current_opcode == 0x05:
            opcodes.dcr('b')
        elif current_opcode == 0x06:
            opcodes.mvi('b')
        elif current_opcode == 0x0a:
            opcodes.ldax('b')
        elif current_opcode == 0x0b:
            opcodes.dcx('b')
        elif current_opcode == 0x0c:
            opcodes.inr('c')
        elif current_opcode == 0x0d:
            opcodes.dcr('c')
        elif current_opcode == 0x0e:
            opcodes.mvi('c')
        elif current_opcode == 0x11:
            opcodes.lxi('d')
        elif current_opcode == 0x13:
            opcodes.inx('d')
        elif current_opcode == 0x15:
            opcodes.dcr('d')
        elif current_opcode == 0x16:
            opcodes.mvi('d')
        elif current_opcode == 0x1a:
            opcodes.ldax('d')
        elif current_opcode == 0x1b:
            opcodes.dcx('d')
        elif current_opcode == 0x1c:
            opcodes.inr('e')
        elif current_opcode == 0x1d:
            opcodes.dcr('e')
        elif current_opcode == 0x1e:
            opcodes.mvi('e')
        elif current_opcode == 0x21:
            opcodes.lxi('h')
        elif current_opcode == 0x23:
            opcodes.inx('h')
        elif current_opcode == 0x25:
            opcodes.dcr('h')
        elif current_opcode == 0x26:
            opcodes.mvi('h')
        elif current_opcode == 0x2b:
            opcodes.dcx('h')
        elif current_opcode == 0x2c:
            opcodes.inr('l')
        elif current_opcode == 0x2d:
            opcodes.dcr('l')
        elif current_opcode == 0x2e:
            opcodes.mvi('l')
        elif current_opcode == 0x31:
            opcodes.lxi('sp')
        elif current_opcode == 0x33:
            opcodes.inx('sp')
        elif current_opcode == 0x3b:
            opcodes.dcx('sp')
        elif current_opcode == 0x3c:
            opcodes.inr('a')
        elif current_opcode == 0x3d:
            opcodes.dcr('a')
        elif current_opcode == 0x3e:
            opcodes.mvi('a')
        elif current_opcode == 0x40:
            opcodes.mov('b', 'b')
            print("DEBUG -- MOV B,B HIT")
            print("--BEGIN REGISTER DUMP")
            print(f"a: {memory.registers['a']} b: {memory.registers['b']} c: {memory.registers['c']}")
            print(f"d: {memory.registers['d']} e: {memory.registers['e']} h: {memory.registers['h']}")
            print(f"l: {memory.registers['l']} sp: {memory.registers['sp']} pc: {memory.registers['pc']}")
            print("--END REGISTER DUMP--")
        elif current_opcode == 0x41:
            opcodes.mov('b', 'c')
        elif current_opcode == 0x42:
            opcodes.mov('b', 'd')
        elif current_opcode == 0x43:
            opcodes.mov('b', 'e')
        elif current_opcode == 0x44:
            opcodes.mov('b', 'h')
        elif current_opcode == 0x45:
            opcodes.mov('b', 'l')
        elif current_opcode == 0x46:
            opcodes.mov('b', 'm')
        elif current_opcode == 0x47:
            opcodes.mov('b', 'a')
        elif current_opcode == 0x48:
            opcodes.mov('c', 'b')
        elif current_opcode == 0x49:
            opcodes.mov('c', 'c')
        elif current_opcode == 0x4a:
            opcodes.mov('c', 'd')
        elif current_opcode == 0x4b:
            opcodes.mov('c', 'e')
        elif current_opcode == 0x4c:
            opcodes.mov('c', 'h')
        elif current_opcode == 0x4d:
            opcodes.mov('c', 'l')
        elif current_opcode == 0x4e:
            opcodes.mov('c', 'm')
        elif current_opcode == 0x4f:
            opcodes.mov('c', 'a')
        elif current_opcode == 0x50:
            opcodes.mov('d', 'b')
        elif current_opcode == 0x51:
            opcodes.mov('d', 'c')
        elif current_opcode == 0x52:
            opcodes.mov('d', 'd')
        elif current_opcode == 0x53:
            opcodes.mov('d', 'e')
        elif current_opcode == 0x5c:
            opcodes.mov('e', 'h')
        elif current_opcode == 0x6f:
            opcodes.mov('l', 'a')
        elif current_opcode == 0x76:
            running = False
        elif current_opcode == 0x77:
            opcodes.mov('m', 'a')
        elif current_opcode == 0xc2:
            opcodes.jnz()
        elif current_opcode == 0xc3:
            opcodes.jmp()
        elif current_opcode == 0xc5:
            opcodes.push_reg('b')
        elif current_opcode == 0xc9:
            opcodes.ret()
        elif current_opcode == 0xcd:
            opcodes.call()
        elif current_opcode == 0xd5:
            opcodes.push_reg('d')
        elif current_opcode == 0xd9:
            opcodes.ret()
        elif current_opcode == 0xdd:
            opcodes.call()
        elif current_opcode == 0xe5:
            opcodes.push_reg('h')
        elif current_opcode == 0xed:
            opcodes.call()
        elif current_opcode == 0xf5:
            opcodes.push_reg('psw')
        elif current_opcode == 0xfd:
            opcodes.call()
        else:
            raise UnrecognizedOpcode(f"Opcode {hex(current_opcode)} not recognized at PC {hex(memory.registers['pc'])}")
        memory.registers['pc'] += 1
