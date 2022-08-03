import pygame

pygame.init()
window = pygame.display.set_mode((224, 256))
pygame.display.set_caption("Space Invaders")

coord_cache = {}
index = 0
for _y in range(0, 224):
    for _x in range(0, 256, 8):
        coord_cache[str(index)] = [_x, _y]
        index += 1


def update(address, data):
    global window
    address -= 0x2400
    # address *= 8
    coords = coord_cache[str(address)]
    #print(f"update: {coords} @ {hex(address)} data: {bin(data)}")
    bits = bin(data)[2:]
    while len(bits) < 8:
        bits = '0' + bits
    for bitindex in range(8):
        x = coords[0] + bitindex
        y = coords[1]
        if bits[bitindex] == '0':
            pygame.draw.line(window, (0x00, 0x00, 0x00), (x, y), (x, y))
        else:
            pygame.draw.line(window, (0xFF, 0xFF, 0xFF), (x, y), (x, y))
    pygame.display.flip()
