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
