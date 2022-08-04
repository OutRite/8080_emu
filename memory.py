import struct

import memory

if False:
    import screen
else:
    print("WARNING: Display is disabled. Modify memory.py from 'if False' to 'if True' to re-enable this.")

ram = {}
registers = {
    'pc': 0x0000,
    'sp': 0x0000,
    'a': 0,
    'b': 0,
    'c': 0,
    'd': 0,
    'e': 0,
    'h': 0,
    'l': 0,
    'zero': 0,
    'parity': 0,
    'sign': 0,
    'carry': 0,
}


def sign(num):
    # Convert unsigned integer to bytes
    num = num.to_bytes(1, 'big')
    # Unpack num as signed integer, return
    return struct.unpack('b', num)[0]


def unsign(num):
    # Convert signed integer into bytes
    num = struct.pack('b', num)
    # Convert bytes into unsigned integer
    return num[0]


def reset_ram():
    global ram
    global registers
    ram = {}
    # Code that fills the screen completely. Useful for testing.
    # for i in range(0x2400, 0x4000):
    #    memory.write_memory(i, 0xff, restricted=True)
    registers = {
        'pc': 0x0000,
        'sp': 0x0000,
        'a': 0,
        'b': 0,
        'c': 0,
        'd': 0,
        'e': 0,
        'h': 0,
        'l': 0,
        'zero': 0,
        'parity': 0,
        'sign': 0,
        'carry': 0,
    }


def read_memory(address):
    try:
        if address < 0x4000:
            return ram[str(address)]
        else:
            return ram[str(address - 0x2000)]
    except KeyError:
        return 0


def write_memory(address, data, restricted=True):
    if restricted:
        if 0x1FFF < address < 0x4000:
            if address > 0x23FF:
                # print(f"updating vram at pc {hex(registers['pc'])}")
                try:
                    screen.update(address, data)
                except NameError:
                    pass  # Display is disabled, so continue.
            ram[str(address)] = data
        if 0x3FFF < address < 0x4400:
            ram[str(address - 0x2000)] = data
    else:  # This should only be used to load data into RAM before execution.
        ram[str(address)] = data


def load_file(address, file_name):
    file = open(file_name, 'rb')
    file_data = file.read()
    file.close()
    current_address = address
    for data in file_data:
        write_memory(current_address, data, restricted=False)
        current_address += 1
