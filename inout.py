import memory

sounds = {
    '0': 0,
    '1': 0,
    '2': 0,
    '3': 0,
    '4': 0,
    '5': 0,
    '6': 0,
    '7': 0,
    '8': 0,
    '9': 0,
    '10': 0,
    '11': 0,
    '12': 0,
    '13': 0,
    '14': 0,
    '15': 0
}
keystate = {
    'coin': 0,
    '2pstart': 0,
    '1pstart': 0,
    '1pshot': 0,
    '1pleft': 0,
    '1pright': 0,
    'tilt': 0,
    '2pleft': 0,
    '2pright': 0,
    '2pshot': 0,
}
dip = {  # Settings for the machine. Change these to change the game.
    '3': 0,
    '5': 0,
    '6': 0,
    '7': 0,
}
shift_data = {
    'x': 0x00,
    'y': 0x00,
    'offset': 0,
}


class UnknownIO(Exception):
    pass


def out(value):
    if value == 2:
        a = memory.registers['a']
        shift_data['offset'] = a & 0b00000111
        print(f"SHIFT OFFSET {shift_data['offset']}")
    elif value == 3:
        # Sounds. TODO: Actual sound emulation
        a = memory.registers['a']
        binary = bin(a)[2:]
        while len(binary) < 8:
            binary = '0' + binary
        for i in range(8):
            sounds[str(i)] = int(binary[i])
            if binary[i] == '0':
                print(f"SFX{i} disabled")
            else:
                print(f"SFX{i} triggered")
    elif value == 4:
        shift_data['y'] = shift_data['x']
        shift_data['x'] = memory.registers['a']
        print(f"New shift data: {shift_data['x']} & {shift_data['y']}")
    elif value == 5:
        # More sounds. TODO: More actual sound emulation
        a = memory.registers['a']
        binary = bin(a)[2:]
        while len(binary) < 8:
            binary = '0' + binary
        for i in range(8):
            sounds[str(i+8)] = int(binary[i])
            if binary[i] == '0':
                print(f"SFX{i+8} disabled")
            else:
                print(f"SFX{i+8} enabled")
    elif value == 6:
        # Watchdog. On a real machine, watchdog will reset the system if it goes
        # too long without receiving a signal, as a crash recovery mechanic.
        # print("Watchdog update!")
        pass
    else:
        raise UnknownIO(f"OUT {value}")


def inp(value):
    if value == 1:
        total = 0
        total += keystate['coin'] << 0
        total += keystate['2pstart'] << 1
        total += keystate['1pstart'] << 2
        total += 1 << 3
        total += keystate['1pshot'] << 4
        total += keystate['1pleft'] << 5
        total += keystate['1pright'] << 6
        memory.registers['a'] = total
    elif value == 2:
        total = 0
        total += dip['3'] << 0
        total += dip['5'] << 1
        total += keystate['tilt'] << 2
        total += dip['6'] << 3
        total += keystate['2pshot'] << 4
        total += keystate['2pleft'] << 5
        total += keystate['2pright'] << 6
        total += dip['7'] << 7
        memory.registers['a'] = total
    elif value == 3:
        xy_data = (shift_data['x'] << 8) + shift_data['y']
        # I don't understand how this works, but it definitely does work.
        memory.registers['a'] = (xy_data >> (8 - shift_data['offset'])) & 0xFF
    else:
        raise UnknownIO(f"IN {value}")