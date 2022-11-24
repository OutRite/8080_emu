display_enabled = False
import memory
import opcodes
import inout
import pygame

rp = {
    '00': 'b',
    '01': 'd',
    '10': 'h',
    '11': 'sp'
}
rp_alt = {
    '00': 'b',
    '01': 'd',
    '10': 'h',
    '11': 'psw'
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
    instruction_count = 0
    long_interrupt = False
    print(f"Booting from address {address}...")
    memory.registers['pc'] = address
    running = True
    while running:
        if display_enabled:  # pragma: no cover
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        inout.keystate['1pleft'] = 1
                    elif event.key == pygame.K_RIGHT:
                        inout.keystate['1pright'] = 1
                    elif event.key == pygame.K_q:
                        inout.keystate['coin'] = 1
                    elif event.key == pygame.K_a:
                        inout.keystate['1pstart'] = 1
                    elif event.key == pygame.K_s:
                        inout.keystate['2pstart'] = 1
                    elif event.key == pygame.K_z:
                        inout.keystate['1pshot'] = 1
                    elif event.key == pygame.K_j:
                        inout.keystate['2pleft'] = 1
                    elif event.key == pygame.K_l:
                        inout.keystate['2pright'] = 1
                    elif event.key == pygame.K_m:
                        inout.keystate['2pshot'] = 1
                    elif event.key == pygame.K_t:
                        inout.keystate['tilt'] = 1
                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT:
                        inout.keystate['1pleft'] = 0
                    elif event.key == pygame.K_RIGHT:
                        inout.keystate['1pright'] = 0
                    elif event.key == pygame.K_q:
                        inout.keystate['coin'] = 0
                    elif event.key == pygame.K_a:
                        inout.keystate['1pstart'] = 0
                    elif event.key == pygame.K_s:
                        inout.keystate['2pstart'] = 0
                    elif event.key == pygame.K_z:
                        inout.keystate['1pshot'] = 0
                    elif event.key == pygame.K_j:
                        inout.keystate['2pleft'] = 0
                    elif event.key == pygame.K_l:
                        inout.keystate['2pright'] = 0
                    elif event.key == pygame.K_m:
                        inout.keystate['2pshot'] = 0
                    elif event.key == pygame.K_t:
                        inout.keystate['tilt'] = 0
        if memory.registers['interrupts'] == 1:
            instruction_count += 1
        if instruction_count == 400 and memory.registers['interrupts'] == 1:  # Estimate.
            if not long_interrupt:
                current_opcode = 0xCF
                # print("SL96 interrupt")
                long_interrupt = True
                instruction_count = 0
            else:
                if display_enabled:  # pragma: no cover
                    pygame.display.flip()
                current_opcode = 0xD7
                # print(f"SL224 interrupt timer={memory.read_memory(0x20c0)}")
                long_interrupt = False
                instruction_count = 0
        else:
            current_opcode = memory.read_memory(memory.registers['pc'])
        # print(f"TRACE pc={hex(memory.registers['pc'])} opc={hex(current_opcode)}")
        # print(f"REGS1 sp={hex(memory.registers['sp'])} a={hex(memory.registers['a'])}")
        # print(f"REGS2 b={hex(memory.registers['b'])} c={hex(memory.registers['c'])} d={hex(memory.registers['d'])}")
        # print(f"REGS3 e={hex(memory.registers['e'])} h={hex(memory.registers['h'])} l={hex(memory.registers['l'])}")
        # print(f"FLAG1 z={memory.registers['zero']} p={memory.registers['parity']} s={memory.registers['sign']}")
        # print(f"FLAG2 c={memory.registers['carry']} a={memory.registers['aux']}")
        # print(f"INTRP {memory.registers['interrupts']} IC={instruction_count} LI={long_interrupt}")
        opcode_bin = bin(current_opcode)[2:]
        while len(opcode_bin) < 8:
            opcode_bin = '0' + opcode_bin
        if opcode_bin == '00000000':
            opcodes.nop()
        elif opcode_bin == '00100111':
            opcodes.daa()
        elif opcode_bin[:2] == '11' and opcode_bin[5:] == '010':  # JUMP INSTRUCTIONS (Except JMP)
            if opcode_bin[2:5] == '000':
                opcodes.jnz()
            elif opcode_bin[2:5] == '001':
                opcodes.jz()
            elif opcode_bin[2:5] == '010':
                opcodes.jnc()
            elif opcode_bin[2:5] == '011':
                opcodes.jc()
            elif opcode_bin[2:5] == '111':
                opcodes.jm()
            elif opcode_bin[2:5] == '101':
                opcodes.jpe()
            elif opcode_bin[2:5] == '110':
                opcodes.jp()
            elif opcode_bin[2:5] == '100':
                opcodes.jpo()
            else:
                raise UnrecognizedOpcode(f"Unknown JUMP {opcode_bin[2:5]} opcode: {current_opcode}")
        elif opcode_bin[:2] == '11' and opcode_bin[5:] == '011':  # JUMP-like INSTRUCTIONS
            if opcode_bin[2:5] == '000' or opcode_bin[2:5] == '001':
                opcodes.jmp()
            elif opcode_bin[2:5] == '010':
                opcodes.out()
            elif opcode_bin[2:5] == '011':
                opcodes.inp()
            elif opcode_bin[2:5] == '101':
                opcodes.xchg()
            elif opcode_bin[2:5] == '100':
                opcodes.xthl()
            elif opcode_bin[2:4] == '11':
                if opcode_bin[4] == '0':
                    opcodes.di()
                else:
                    opcodes.ei()
            else:
                raise UnrecognizedOpcode(f"Unknown JUMP-like {opcode_bin[2:5]} opcode: {current_opcode}")
        elif opcode_bin[:2] == '00' and opcode_bin[4:] == '0001':
            opcodes.lxi(rp[opcode_bin[2:4]])
        elif opcode_bin[:2] == '00' and opcode_bin[5:] == '110':
            opcodes.mvi(reg[opcode_bin[2:5]])
        elif opcode_bin == '11001101':
            opcodes.call()
        elif opcode_bin[:2] == '11' and opcode_bin[5:] == '100':
            if opcode_bin[2:5] == '011':
                opcodes.cc()
            elif opcode_bin[2:5] == '100':
                opcodes.cpo()
            elif opcode_bin[2:5] == '111':
                opcodes.cm()
            elif opcode_bin[2:5] == '000':
                opcodes.cnz()
            elif opcode_bin[2:5] == '010':
                opcodes.cnc()
            elif opcode_bin[2:5] == '101':
                opcodes.cpe()
            elif opcode_bin[2:5] == '110':
                opcodes.cp()
            elif opcode_bin[2:5] == '001':
                opcodes.cz()
            else:
                raise UnrecognizedOpcode(f"Unknown CALL-like {opcode_bin[2:5]} opcode: {current_opcode}")
        elif opcode_bin[:2] == '00' and opcode_bin[4:] == '1011':
            opcodes.dcx(rp[opcode_bin[2:4]])
        elif opcode_bin[:3] == '000' and opcode_bin[4:] == '1010':
            if opcode_bin[3] == '0':
                opcodes.ldax('b')
            else:
                opcodes.ldax('d')
        elif opcode_bin[:3] == '000' and opcode_bin[4:] == '0010':
            if opcode_bin[3] == '0':
                opcodes.stax('b')
            else:
                opcodes.stax('d')
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
        elif opcode_bin[:2] == '00' and opcode_bin[5:] == '100':
            opcodes.inr(reg[opcode_bin[2:5]])
        elif opcode_bin[:2] == '11' and opcode_bin[5:] == '000':
            if opcode_bin[2:5] == '001':
                opcodes.rz()
            elif opcode_bin[2:5] == '000':
                opcodes.rnz()
            elif opcode_bin[2:5] == '010':
                opcodes.rnc()
            elif opcode_bin[2:5] == '011':
                opcodes.rc()
            elif opcode_bin[2:5] == '101':
                opcodes.rpe()
            elif opcode_bin[2:5] == '100':
                opcodes.rpo()
            elif opcode_bin[2:5] == '111':
                opcodes.rm()
            elif opcode_bin[2:5] == '110':
                opcodes.rp()
            else:
                raise UnrecognizedOpcode(f"Unknown RETURN {opcode_bin[2:5]} opcode: {current_opcode}")
        elif opcode_bin[:2] == '11' and opcode_bin[5:] == '001':
            if opcode_bin[2:5] == '001':
                opcodes.ret()
            elif opcode_bin[2:5] == '101':
                opcodes.pchl()
            elif opcode_bin[4] == '0':
                opcodes.pop_reg(rp_alt[opcode_bin[2:4]])
            elif opcode_bin[2:5] == '111':
                opcodes.sphl()
            else:
                raise UnrecognizedOpcode(f"Unknown RETURN-like {opcode_bin[2:5]} opcode: {current_opcode}")
        elif opcode_bin[:2] == '11' and opcode_bin[5:] == '110':
            if opcode_bin[2:5] == '111':
                opcodes.cpi()
            elif opcode_bin[2:5] == '100':
                opcodes.ani()
            elif opcode_bin[2:5] == '101':
                opcodes.xri()
            elif opcode_bin[2:5] == '000':
                opcodes.adi()
            elif opcode_bin[2:5] == '010':
                opcodes.sui()
            elif opcode_bin[2:5] == '001':
                opcodes.aci()
            elif opcode_bin[2:5] == '011':
                opcodes.sbi()
            elif opcode_bin[2:5] == '110':
                opcodes.ori()
        elif opcode_bin[:2] == '11' and opcode_bin[4:] == '0101':
            opcodes.push_reg(rp_alt[opcode_bin[2:4]])
        elif opcode_bin[:2] == '00' and opcode_bin[4:] == '1001':
            opcodes.dad(rp[opcode_bin[2:4]])
        elif opcode_bin[:3] == '000' and opcode_bin[5:] == '111':
            if opcode_bin[3:5] == '01':
                opcodes.rrc()
            elif opcode_bin[3:5] == '00':
                opcodes.rlc()
            elif opcode_bin[3:5] == '10':
                opcodes.ral()
            elif opcode_bin[3:5] == '11':
                opcodes.rar()
        elif opcode_bin[:3] == '001' and opcode_bin[5:] == '010':
            if opcode_bin[3:5] == '11':
                opcodes.lda()
            elif opcode_bin[3:5] == '10':
                opcodes.sta()
            elif opcode_bin[3:5] == '01':
                opcodes.lhld()
            elif opcode_bin[3:5] == '00':
                opcodes.shld()
        elif opcode_bin[:2] == '10':
            if opcode_bin[2:5] == '101':
                opcodes.xra(reg[opcode_bin[5:]])
            elif opcode_bin[2:5] == '100':
                opcodes.ana(reg[opcode_bin[5:]])
            elif opcode_bin[2:5] == '110':
                opcodes.ora(reg[opcode_bin[5:]])
            elif opcode_bin[2:5] == '001':
                opcodes.adc(reg[opcode_bin[5:]])
            elif opcode_bin[2:5] == '000':
                opcodes.add(reg[opcode_bin[5:]])
            elif opcode_bin[2:5] == '010':
                opcodes.sub(reg[opcode_bin[5:]])
            elif opcode_bin[2:5] == '011':
                opcodes.sbb(reg[opcode_bin[5:]])
            elif opcode_bin[2:5] == '111':
                opcodes.cmp(reg[opcode_bin[5:]])
        elif opcode_bin[:2] == '11' and opcode_bin[5:] == '111':
            opcodes.rst((current_opcode & 0b00111000) >> 3)
        elif opcode_bin[:4] == '0011' and opcode_bin[5:] == '111':
            if opcode_bin[4] == '0':
                opcodes.stc()
            else:
                opcodes.cmc()
        elif opcode_bin == '00101111':
            opcodes.cma()
        else:
            raise UnrecognizedOpcode(f"Opcode {hex(current_opcode)} not recognized at PC {hex(memory.registers['pc'])}")
        memory.registers['pc'] += 1
