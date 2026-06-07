import pygame
import math
import random
import sys

PW, PH = 160, 90
SCALE = 8
WIN_W = PW * SCALE
WIN_H = PH * SCALE
FPS = 60
TWINKLE_INTERVAL = 20

#hex를 rgb로
def h(hex_str):
    hex_str = hex_str.lstrip('#')
    return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))

#전체밝기조절
BRIGHTNESS = 0.3

def dim(hex_str, factor=None):
    if factor is None:
        factor = BRIGHTNESS
    hex_str = hex_str.lstrip('#')
    r, g, b = (int(hex_str[i:i+2], 16) for i in (0, 2, 4))
    return (int(r * factor), int(g * factor), int(b * factor))

C = {
    'bg0':    dim('020714', 1.0),
    'bg1':    dim('050d24', 0.8),
    'nebula1':dim('0f0620', 1.0),
    'nebula2':dim('060f1e', 1.0),
    'nebula3':dim('1a0608', 1.0),

    'star1':  dim('ffffff', 1.0),
    'star2':  dim('ffe8c0', 1.0),
    'star3':  dim('c0d8ff', 1.0),
    'star4':  dim('ffc0c0', 1.0),
    'starDim':dim('334455', 1.0),

    'planet1': dim('7b5ea7'),
    'planet1l':dim('b08fd4'),
    'planet1d':dim('3d2a5e'),
    'planet2': dim('5ea77b'),
    'planet2l':dim('8fd4b0'),
    'planet2d':dim('2a5e3d'),
    'moon':    dim('c8c8d8'),
    'moonl':   dim('eeeef8'),
    'moond':   dim('888898'),
    'ring':    dim('c4a35a'),
    'ringl':   dim('e8d090'),
    'ringd':   dim('7a5e20'),
    'comet':   dim('ddeeff'),
    'cometT':  dim('88aacc'),
    'ufo':     dim('88ffcc'),
    'ufoD':    dim('226644'),
    'ufoG':    dim('ffff88'),
    'rocket':  dim('ff8844'),
    'rocketW': dim('ffffff'),
    'rocketR': dim('ff3333'),
    'aster':   dim('8877aa'),
    'asterD':  dim('443355'),
    'yellow':  dim('ffff44'),
    'ufoW':    dim('aaffee'),
}


def setpx(surf, x, y, col):
    if 0 <= x < PW and 0 <= y < PH:
        surf.set_at((x, y), col)

def fill_rect(surf, x, y, w, h, col):
    for dy in range(h):
        for dx in range(w):
            setpx(surf, x + dx, y + dy, col)

def draw_bg(surf):
    for y in range(PH):
        for x in range(PW):
            nx = x / PW
            ny = y / PH
            n1 = math.sin(nx * 6.3 + 1.2) * math.cos(ny * 4.1)
            n2 = math.sin(nx * 3.1 + ny * 5.7 + 0.8)
            if   n1 > 0.55:              col = C['nebula1']
            elif n2 > 0.6:               col = C['nebula2']
            elif n1 < -0.6 and n2 > 0.1: col = C['nebula3']
            elif ny < 0.3 and nx > 0.5:  col = C['bg1']
            else:                         col = C['bg0']
            surf.set_at((x, y), col)

#별
STAR_DATA = [
    (18,8,2),(83,4,2),(126,7,2),(50,1,1),(158,5,1),
    (5,15,2),(48,15,2),(92,17,2),(157,17,2),
    (14,28,2),(57,24,2),(100,21,2),(144,27,2),
    (2,35,2),(46,32,2),(89,39,2),(138,31,0),
    (9,42,2),(53,49,2),(97,44,2),(140,41,2),
    (5,55,2),(54,59,0),(114,53,2),(158,56,2),
    (20,64,2),(64,61,2),(119,66,0),(157,66,1),
    (3,75,2),(52,79,0),(96,74,0),(145,77,1),
    (22,84,2),(66,81,2),(110,87,0),(155,83,0),
    (37,13,1),(103,12,1),(117,26,0),(133,24,1),
    (35,33,1),(105,37,0),(20,44,1),(124,42,0),
    (16,58,1),(76,53,0),(31,67,1),(108,67,0),
    (14,78,1),(85,72,0),(33,87,1),(99,84,0),
]

STAR_COLORS = ['star1', 'star2', 'star3', 'star4']

def draw_stars(surf):
    for (sx, sy, stype) in STAR_DATA:
        ci = (sx * 3 + sy * 7) % len(STAR_COLORS)
        col = C[STAR_COLORS[ci]]
        dim = C['starDim']
        if stype == 0:
            setpx(surf, sx, sy, col)
        elif stype == 1:
            setpx(surf, sx,   sy,   col)
            setpx(surf, sx-1, sy,   dim)
            setpx(surf, sx+1, sy,   dim)
            setpx(surf, sx,   sy-1, dim)
            setpx(surf, sx,   sy+1, dim)
        elif stype == 2:
            setpx(surf, sx,   sy,   col)
            setpx(surf, sx-1, sy,   col)
            setpx(surf, sx+1, sy,   col)
            setpx(surf, sx,   sy-1, col)
            setpx(surf, sx,   sy+1, col)
            setpx(surf, sx-2, sy,   dim)
            setpx(surf, sx+2, sy,   dim)
            setpx(surf, sx,   sy-2, dim)
            setpx(surf, sx,   sy+2, dim)

def draw_planet1(surf, cx, cy, r):
    
    for dx in range(-r-6, r+7):
        ry = round(abs(dx) * 0.25)
        if abs(dx) > r - 1:
            setpx(surf, cx+dx, cy+ry-1, C['ring'])
            setpx(surf, cx+dx, cy+ry,   C['ringl'])
            setpx(surf, cx+dx, cy+ry+1, C['ringd'])
    
    for dy in range(-r, r+1):
        for dx in range(-r, r+1):
            dist = dx*dx + dy*dy
            if dist <= r*r:
                nx2 = dx / r
                ny2 = dy / r
                light = -nx2*0.5 - ny2*0.5
                if   dist > (r-1)*(r-1): col = C['planet1d']
                elif light < -0.2:        col = C['planet1l']
                else:                     col = C['planet1']
                setpx(surf, cx+dx, cy+dy, col)
    
    for dx in range(-r-6, -r+3):
        ry = round(abs(dx) * 0.25)
        setpx(surf, cx+dx, cy+ry-1, C['ring'])
        setpx(surf, cx+dx, cy+ry,   C['ringl'])
        setpx(surf, cx+dx, cy+ry+1, C['ringd'])
    for dx in range(r-2, r+7):
        ry = round(abs(dx) * 0.25)
        setpx(surf, cx+dx, cy+ry-1, C['ring'])
        setpx(surf, cx+dx, cy+ry,   C['ringl'])
        setpx(surf, cx+dx, cy+ry+1, C['ringd'])

def draw_planet2(surf, cx, cy, r):
    for dy in range(-r, r+1):
        for dx in range(-r, r+1):
            dist = dx*dx + dy*dy
            if dist <= r*r:
                nx2 = dx / r
                ny2 = dy / r
                light = -nx2*0.5 - ny2*0.5
                if   dist > (r-1)*(r-1): col = C['planet2d']
                elif light < -0.3:        col = C['planet2l']
                else:                     col = C['planet2']
                setpx(surf, cx+dx, cy+dy, col)
    setpx(surf, cx-1, cy-1, C['planet2l'])
    setpx(surf, cx+1, cy-1, C['planet2l'])
    setpx(surf, cx-1, cy+1, C['planet2d'])
    setpx(surf, cx,   cy+1, C['planet2d'])
    setpx(surf, cx+1, cy+1, C['planet2d'])

def draw_moon(surf, cx, cy, r):
    for dy in range(-r, r+1):
        for dx in range(-r, r+1):
            dist = dx*dx + dy*dy
            if dist <= r*r:
                if   dist > (r-1)*(r-1):   col = C['moond']
                elif dx < -1 and dy < -1:   col = C['moonl']
                else:                       col = C['moon']
                setpx(surf, cx+dx, cy+dy, col)
    setpx(surf, cx+1, cy+1, C['moond'])
    setpx(surf, cx+2, cy+1, C['moond'])
    setpx(surf, cx-1, cy+2, C['moond'])

def draw_ufo(surf, cx, cy):
    fill_rect(surf, cx-2, cy-3, 5, 2, C['ufo'])
    setpx(surf, cx-1, cy-4, C['ufo'])
    setpx(surf, cx,   cy-4, C['ufo'])
    setpx(surf, cx+1, cy-4, C['ufo'])
    setpx(surf, cx,   cy-5, C['moonl'])
    fill_rect(surf, cx-4, cy-2, 9, 3, C['ufo'])
    setpx(surf, cx-5, cy-1, C['ufoD'])
    setpx(surf, cx+5, cy-1, C['ufoD'])
    fill_rect(surf, cx-3, cy+1, 7, 1, C['ufoG'])
    setpx(surf, cx-2, cy+2, C['ufoG'])
    setpx(surf, cx,   cy+2, C['ufoG'])
    setpx(surf, cx+2, cy+2, C['ufoG'])
    setpx(surf, cx,   cy-2, C['ufoG'])
    setpx(surf, cx-1, cy-2, C['ufoW'])

def draw_comet(surf, cx, cy):
    for i in range(12):
        if   i < 4: col = C['comet']
        elif i < 8: col = C['cometT']
        else:       col = C['starDim']
        setpx(surf, cx - i, cy, col)
        if i > 2:
            setpx(surf, cx - i + 1, cy - 1, col)
            setpx(surf, cx - i + 1, cy + 1, col)
    setpx(surf, cx,   cy,   C['star1'])
    setpx(surf, cx+1, cy,   C['star1'])
    setpx(surf, cx,   cy-1, C['comet'])
    setpx(surf, cx,   cy+1, C['comet'])

def draw_rocket(surf, cx, cy):
    setpx(surf, cx,   cy,   C['rocketW'])
    setpx(surf, cx-1, cy+1, C['rocketW'])
    setpx(surf, cx,   cy+1, C['rocketW'])
    setpx(surf, cx+1, cy+1, C['rocketW'])
    fill_rect(surf, cx-1, cy+2, 3, 4, C['rocketW'])
    setpx(surf, cx, cy+3, C['star3'])
    setpx(surf, cx-2, cy+5, C['rocketR'])
    setpx(surf, cx-2, cy+6, C['rocketR'])
    setpx(surf, cx+2, cy+5, C['rocketR'])
    setpx(surf, cx+2, cy+6, C['rocketR'])
    setpx(surf, cx-1, cy+6, C['rocket'])
    setpx(surf, cx,   cy+6, C['yellow'])
    setpx(surf, cx+1, cy+6, C['rocket'])
    setpx(surf, cx,   cy+7, C['rocket'])
    setpx(surf, cx-1, cy+7, C['starDim'])
    setpx(surf, cx+1, cy+7, C['starDim'])

def draw_asteroid(surf, cx, cy):
    outline = [(0,-2),(1,-2),(2,-1),(2,0),(1,1),(0,2),(-1,1),(-2,0),(-2,-1),(-1,-2)]
    for dx, dy in outline:
        setpx(surf, cx+dx, cy+dy, C['asterD'])
    for dy in range(-1, 2):
        for dx in range(-1, 2):
            setpx(surf, cx+dx, cy+dy, C['aster'])
    setpx(surf, cx-1, cy-1, C['asterD'])
    setpx(surf, cx+1, cy,   C['asterD'])

def draw_shooting_star(surf, x1, y1, length):
    for i in range(length):
        if   i < 3:  col = C['star1']
        elif i < 6:  col = C['star2']
        elif i < 10: col = C['cometT']
        else:        col = C['starDim']
        setpx(surf, x1 + i, y1 - i, col)

def draw_constellation_line(surf, x1, y1, x2, y2):
    dx = x2 - x1
    dy = y2 - y1
    steps = max(abs(dx), abs(dy))
    if steps == 0:
        return
    for i in range(steps + 1):
        x = round(x1 + dx * i / steps)
        y = round(y1 + dy * i / steps)
        if i % 2 == 0:
            setpx(surf, x, y, C['starDim'])

def draw_scene(surf):
    draw_bg(surf)

    draw_constellation_line(surf, 10,20, 18,14)
    draw_constellation_line(surf, 18,14, 28,18)
    draw_constellation_line(surf, 28,18, 22,25)
    draw_constellation_line(surf, 22,25, 10,20)
    draw_constellation_line(surf, 120,60, 130,55)
    draw_constellation_line(surf, 130,55, 140,62)
    draw_constellation_line(surf, 140,62, 135,70)

    draw_stars(surf)

    draw_shooting_star(surf, 40, 15, 14)
    draw_shooting_star(surf, 100, 30, 10)
    draw_shooting_star(surf, 130, 10, 12)

    draw_planet1(surf, 126, 22, 12)
    draw_planet2(surf, 24, 68, 7)
    draw_moon(surf, 45, 42, 6)
    draw_ufo(surf, 35, 20)
    draw_rocket(surf, 140, 62)
    draw_asteroid(surf, 80, 55)
    draw_asteroid(surf, 92, 72)
    draw_comet(surf, 110, 45)
    draw_comet(surf, 65, 30)

    setpx(surf, 50, 1, C['star1'])
    setpx(surf, 83, 4, C['star1'])
    setpx(surf, 38, 9, C['star1'])
    setpx(surf, 18, 8, C['star1'])


TWINKLE_STARS = [
    (38,9),(83,4),(104,8),(148,3),
    (27,11),(92,17),(140,21),
    (100,21),(124,16),
    (9,42),(75,43),(113,43),
]

def apply_twinkle(surf):
    for (sx, sy) in TWINKLE_STARS:
        if random.random() > 0.5:
            if random.random() > 0.5:
                col  = C['star1']
                arm  = C['star2']
            else:
                col  = C['starDim']
                arm  = C['bg0']
            setpx(surf, sx,   sy,   col)
            setpx(surf, sx-1, sy,   arm)
            setpx(surf, sx+1, sy,   arm)
            setpx(surf, sx,   sy-1, arm)
            setpx(surf, sx,   sy+1, arm)


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIN_W, WIN_H))
    pygame.display.set_caption("픽셀 우주 배경화면")
    clock = pygame.time.Clock()

    pixel_surf = pygame.Surface((PW, PH))

    draw_scene(pixel_surf)

    frame = 0
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        frame += 1
        if frame % TWINKLE_INTERVAL == 0:
            draw_scene(pixel_surf)
            apply_twinkle(pixel_surf)

        scaled = pygame.transform.scale(pixel_surf, (WIN_W, WIN_H))
        screen.blit(scaled, (0, 0))
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()