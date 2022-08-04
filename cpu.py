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
                raise UnrecognizedOpcode(f"Unknown JUMP {opcode_bin[2:5]} opcode: {current_opcode}")
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
                raise UnrecognizedOpcode(f"Unknown RETURN {opcode_bin[2:5]} opcode: {current_opcode}")
        elif opcode_bin[:2] == '11' and opcode_bin[5:] == '110':
            if opcode_bin[2:5] == '111':
                opcodes.cpi()
            else:
                raise UnrecognizedOpcode(f"Unknown IMMEDIATE {opcode_bin[2:5]} opcode: {current_opcode}")
        else:
            raise UnrecognizedOpcode(f"Opcode {hex(current_opcode)} not recognized at PC {hex(memory.registers['pc'])}")
        memory.registers['pc'] += 1
