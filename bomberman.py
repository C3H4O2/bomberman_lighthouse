# Abgabe als Gruppe Emil^2
# Gruppenmitglieder: Emil Büttner, Emil Wiards

# Imports
import random
from config import UNAME, TOKEN
from math import sqrt
import os
import sys
import pygame

from pyghthouse import Pyghthouse, VerbosityLevel, KeyEvent
ph = Pyghthouse(UNAME, TOKEN, verbosity=VerbosityLevel.NONE, stream_remote_inputs=True)
ph.start()

pygame.init()

# size and color constants
aw, ah = 840, 660
dx, dy = 30, 60
w, h = aw//dx - 3, ah//dy - 2
ah += dy*3
FPS = 60  # Frames per second.

BLACK = (0, 0, 0)
GRAY = (150, 150, 150)
WHITE = (255, 255, 255)
PURPLE = (233, 182, 236)
RED = (255, 0, 0)
ORANGE = (255, 69, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BROWN = (202, 164, 114)
PUCOL1 = (164, 198, 57)
PUCOL2 = (153, 102, 204)
PUCOL3 = (127, 255, 212)

# Pygame screen and clock initialisation
screen = pygame.display.set_mode((aw, ah))
clock = pygame.time.Clock()


# Frames till a bomb explodes after being planted
bt = 200


# Basic Object class with position and color attributes
# and a individual timer used for drawing
class Object:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.st = 30

# Powerup class:
#   init: random choice for attribute to power up
#   draw: displays Powerup blinking
class Powerup(Object):
    def __init__(self, x, y):
        r = random.random()
        if r<=1/3:
            self.pu = 0
            super().__init__(x,y,PUCOL1)
        elif r<=2/3:
            self.pu = 1
            super().__init__(x,y,PUCOL2)
        else:
            self.pu = 2
            super().__init__(x,y,PUCOL3)
        self.dcol = self.color

    def draw(self):
        self.st -= 1
        if self.st==0:
            if self.color == BLACK:
                self.color = self.dcol
            else:
                self.color = BLACK
            self.st = 30
            
# Bomb class:
#   init: sets behaviour matching the planters attributes
#   draw: displays bomb blinking exponenitonally faster until the bomb explodes
class Bomb(Object):
    def __init__(self, x, y, strength):
        super().__init__(x, y, RED)
        self.strength = strength
        self.exp = bt
        self.st = self.exp - int(sqrt(self.exp))
    
    def draw(self):
        global img
        self.exp -= 1

        if self.exp <= 10:
            self.color = RED
        else:
            if self.exp == self.st:
                if self.color == RED:
                    self.color = GRAY
                else:
                    self.color = RED
                self.st = self.exp - int(sqrt(self.exp))

        pygame.draw.rect(screen, self.color, (self.x*dx, self.y*dy, dx, dy), 0)
        img[self.y][self.x] = self.color

# Explosion class:
#   init: affected positions are calculated according to parameters of bomb
#   collision: checks for nearby bombs (initialises explosion),
#       boxes (destroys boxes) and checks for objects in the way
#   death: checks if a player is or moves into the explosion
#   draw: displays the explosion
class Explosion(Object):
    def __init__(self, b):
        super().__init__(b.x, b.y, ORANGE)
        self.strength = b.strength
        self.exp = 60
        self.vis = [(self.x, self.y)]

        for xi in range(self.x, self.x+self.strength+1):
            if self.collision(xi, self.y): break
        for xi in range(self.x, self.x-self.strength-1,-1):
            if self.collision(xi, self.y): break
        for yi in range(self.y, self.y+self.strength+1):
            if self.collision(self.x, yi): break
        for yi in range(self.y, self.y-self.strength-1,-1):
            if self.collision(self.x, yi): break

    def collision(self, x, y):
        if (x,y) != (self.x,self.y):
            if any([x==oi.x and y==oi.y for oi in o]):
                return 1

            self.vis.append((x, y))

            for i in range(len(bx)):
                if x==bx[i].x and y==bx[i].y:
                    if random.random()<0.2:
                        pu.append(Powerup(bx[i].x, bx[i].y))
                    bx.pop(i)
                    return 1
            
            for i in range(len(b)):
                if b[i].x==x and b[i].y==y:
                    b[i].exp = 1


            return 0
    def death(self, x, y):
        for i in range(2):
            if p[i].x==x and p[i].y==y:
                dead[i] = True


    def draw(self):
        global img
        self.exp -= 1

        for i in self.vis:
            pygame.draw.rect(screen, self.color, (i[0]*dx, i[1]*dy, dx, dy), 0)
            img[i[1]][i[0]] = self.color
            self.death(i[0], i[1])

# Player class:
#   init: set starting attributes
#   move: moves the player in the specified direction
#   plant: plants a bomb at the current location of the player
class Player(Object):
    def __init__(self, x, y, color, keyset):
        super().__init__(x, y, color)
        self.keyset = keyset
        self.timeout = 15
        self.next_move = self.timeout
        self.exp_strength = 2
        self.bombs = 1
        self.bombtimers = []

    def move(self, Dx, Dy):
        if (all([pi.x != self.x+Dx or pi.y != self.y+Dy for pi in p]) and
            all([oi.x != self.x+Dx or oi.y != self.y+Dy for oi in o+bx+b]) and
            not (self.x+Dx<0 or self.x+Dx>=w) and
            not (self.y+Dy<0 or self.y+Dy>=h)):

            self.x += Dx
            self.y += Dy
            for pui in pu:
                if self.x==pui.x and self.y==pui.y:
                    if pui.pu == 0:
                        self.bombs = min(self.bombs+1, 6)
                    elif pui.pu == 1:
                        self.exp_strength = min(self.exp_strength + 1, 7)
                    else:
                        self.timeout = max(self.timeout-1, 10)
                    pu.remove(pui)
                    break

        
    def plant(self):
        if not any([self.x==bi.x and self.y==bi.y for bi in b]):
            if self.bombs>0:
                self.bombs -= 1
                self.bombtimers.append(bt)
                b.append(Bomb(self.x, self.y, self.exp_strength))


# actions function: handles keys actions regarding the movement
def actions():
    for j, pi in enumerate(p):
        if pi.next_move <= t:
            tx, ty = pi.x, pi.y
            moved = False
            for i in keys[::-1]:
                if pi.keyset[0] == i:
                    pi.move(0, -1)
                    moved = True
                    break
                elif pi.keyset[1] == i:
                    pi.move(0, 1)
                    moved = True
                    break
                elif pi.keyset[2] == i:
                    pi.move(-1, 0)
                    moved = True
                    break
                elif pi.keyset[3] == i:
                    pi.move(1, 0)
                    moved = True
                    break
            if moved:
                pi.next_move = t + pi.timeout
                lp[j] = [tx, ty]
                mat[j] = matd


# draw function: displays everything in local pygame window
#   and via lighthouse api.
#   Additionally some interaction behaviour between certain object ist set here
def draw():
    global img
    for oi in o+bx:
        pygame.draw.rect(screen, oi.color, (oi.x*dx, oi.y*dy, dx, dy), 0)
        img[oi.y][oi.x] = oi.color

    for i in range(2):
        if mat[i]>0:
            col = tuple([int((mat[i]/matd)*j) for j in p[i].color])
            pygame.draw.rect(screen, col, (lp[i][0]*dx, lp[i][1]*dy, dx, dy), 0)
            img[lp[i][1]][lp[i][0]] = col
            mat[i]-=1

    for pi in p:
        pygame.draw.rect(screen, pi.color, (pi.x*dx, pi.y*dy, dx, dy), 0)
        img[pi.y][pi.x] = pi.color

        pl = []
        for i in range(len(pi.bombtimers)):
            if pi.bombtimers[i] == 0:
                pl.append(i)
                pi.bombs += 1
            else:
                pi.bombtimers[i] -= 1
        for i in pl:
            pi.bombtimers.pop(i)


    for pui in pu:
        pygame.draw.rect(screen, pui.color, (pui.x*dx, pui.y*dy, dx, dy), 0)
        img[pui.y][pui.x] = pui.color
        pui.draw()

    pl = []
    for idx, bi in enumerate(b):
        bi.draw()
        if bi.exp == 0:
            pl.append(bi)
            e.append(Explosion(bi))
    for i in pl:
        b.remove(i)



    pl = []
    for idx, ei in enumerate(e):
        ei.draw()
        if ei.exp == 0:
            pl.append(ei)
    for i in pl:
        e.remove(i)

    for i in range(p1.bombs):
        pygame.draw.rect(screen, PUCOL1, (2*i*dx, h*dy, dx, dy), 0)
        img[h][2*i] = PUCOL1
    for i in range(len(p1.bombtimers)):
        pygame.draw.rect(screen, GRAY, (2*(p1.bombs+i)*dx, h*dy, dx, dy), 0)
        img[h][2*(p1.bombs+i)] = GRAY
    for i in range(p1.exp_strength-1):
        pygame.draw.rect(screen, PUCOL2, (2*i*dx, (h+1)*dy, dx, dy), 0)
        img[h+1][2*i] = PUCOL2
    for i in range(abs(p1.timeout-16)):
        pygame.draw.rect(screen, PUCOL3, (2*i*dx, (h+2)*dy, dx, dy), 0)
        img[h+2][2*i] = PUCOL3

    for i in range(p2.bombs):
        pygame.draw.rect(screen, PUCOL1, ((w-2*i-1)*dx, h*dy, dx, dy), 0)
        img[h][w-2*i-1] = PUCOL1
    for i in range(len(p2.bombtimers)):
        pygame.draw.rect(screen, GRAY, ((w-2*(p2.bombs+i)-1)*dx, h*dy, dx, dy), 0)
        img[h][(w-2*(p2.bombs+i)-1)] = GRAY
    for i in range(p2.exp_strength-1):
        pygame.draw.rect(screen, PUCOL2, ((w-2*i-1)*dx, (h+1)*dy, dx, dy), 0)
        img[h+1][w-2*i-1] = PUCOL2
    for i in range(abs(p2.timeout-16)):
        pygame.draw.rect(screen, PUCOL3, ((w-2*i-1)*dx, (h+2)*dy, dx, dy), 0)
        img[h+2][w-2*i-1] = PUCOL3


# init function: initialises box and object positions
def init():
    if len(sys.argv) == 2:
        if read_map(sys.argv[-1]):
            return
    elif len(sys.argv) > 2:
        print("Invalid argument(s)! Starting standard map.")

    for xi in range(2, w-2, 2):
        for yi in range(2, h-2, 2):
            o.append(Object(xi, yi, WHITE))
    for xi in range(w):
        o.append(Object(xi, 0, WHITE))
        o.append(Object(xi, h-1, WHITE))
    for yi in range(1,h-1):
        o.append(Object(0, yi, WHITE))
        o.append(Object(w-1, yi, WHITE))

    for yi in range(1, h-1):
        if not yi in range(2, h-2, 2):
            for xi in range(2, w-2):
                bx.append(Object(xi, yi, BROWN))

# reads custom made map
def read_map(map_path):

    for xi in range(w):
        o.append(Object(xi, 0, WHITE))
        o.append(Object(xi, h-1, WHITE))
    for yi in range(1,h-1):
        o.append(Object(0, yi, WHITE))
        o.append(Object(w-1, yi, WHITE))

    with open(map_path) as f:
        gmap = [i[:23] for i in f.readlines()[:7]]

    if not all(i in "".join(gmap) for i in "12"):
        return False

    print(gmap)
    global p1
    global p2
    global p
    global lp
    for y in range(len(gmap)):
        for x in range(len(gmap[y])):
            if gmap[y][x] == "X":
                o.append(Object(x+1, y+1, WHITE))
            elif gmap[y][x] == "B":
                bx.append(Object(x+1, y+1, BROWN))
            elif gmap[y][x] == "1":
                p1 = Player(x+1, y+1, PURPLE, [pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d, pygame.K_SPACE])
            elif gmap[y][x] == "2":
                p2 = Player(x+1, y+1, GREEN, [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT, 1073742052])
    p = [p1, p2]
    lp = [[0, 0], [w-1, h-1]]

    return True

# reset function: resets  all variables
def reset():
    global p1
    global p2
    global p
    global o
    global b
    global bx
    global e
    global pu
    global dead
    global t
    global keys
    global img

    img = ph.empty_image()

    keys = []
    p1, p2 = Player(1,1, PURPLE, [pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d, pygame.K_SPACE]), Player(w-2, h-2, GREEN, [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT, 1073742052])
    p = [p1, p2]

    o = []
    b = []
    bx = []
    e = []
    pu = []

    dead = [False, False]

    t = 0

    init()


# keyremapping for online key input
cc = [1073741906, 1073741906, 1073741905, 1073741905, 1073741904,
      1073741903, 1073741904, 1073741903, 98, 97]
key_remap = {
    65: 97,          # A
    68: 100,         # D
    87: 119,         # W
    83: 115,         # S
    32: 32,          # SPACE
    37: 1073741904,  # LEFT
    38: 1073741906,  # UP
    40: 1073741905,  # DOWN
    39: 1073741903,  # RIGHT
    17: 1073742052,  # RCTRL
    82: 114,         # R
    66: 98,         # B
}


# developer tools
def opt():
    global ph
    try:
        import placeholder
    except: 
        pass

# first variable initialisation
p1, p2 = (Player(1,1, PURPLE, [pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d, pygame.K_SPACE]),
          Player(w-2, h-2, GREEN, [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT, 1073742052]))
p = [p1, p2]
o = []
b = []
bx = []
e = []
pu = []

dead = [False, False]

t = 0

img = ph.empty_image()

keys = []
lp = [[0,0],[w-1,h-1]]
mat = [0,0]
matd = 7
queue = [0]*10

init()

# shifting image to be centered on lighthouse
def center_img(img):
    ret = [[[0,0,0]]*28] + img[:-1]
    for i in range(len(ret)):
        ret[i] = [[0,0,0]] + ret[i][:-1]

    return ret


# main loop
while True:
    clock.tick(FPS)

    # pygame event loop for local keyboard inputs
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            os._exit(0)
            quit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                reset()
            elif event.key == pygame.K_ESCAPE:
                pygame.quit()
                ph.stop()
                os._exit(0)
                exit()
            queue.append(event.key)
            queue.pop(0)
            if queue == cc:
                ph.stop()
                opt()
                ph.start()
            keys.append(event.key)
            for pi in p:
                if pi.keyset[4] in keys:
                    pi.plant()
        elif event.type == pygame.KEYUP:
            try:
                keys.remove(event.key)
            except:
                pass

    # pyghthouse event loop for remote keyboard inputs - experimental and new pyghthouse feature
    for event in ph.get_all_events():
        if isinstance(event, KeyEvent):
            if event.down:
                if event.code == 82:
                    reset()
                if event.code in key_remap:
                    queue.append(key_remap[event.code])
                    queue.pop(0)
                if queue == cc:
                    ph.stop()
                    opt()
                    ph.start()
                if event.code in key_remap:
                    keys.append(key_remap[event.code])
                for pi in p:
                    if pi.keyset[4] in keys:
                        pi.plant()
            else:
                try:
                    if event.code in key_remap:
                        keys.remove(key_remap[event.code])
                except:
                    pass

    # GAME OVER screen + behaviour
    if not any(dead):
        screen.fill(BLACK)
        img = ph.empty_image()

        actions()

        draw()
    else:
        if all(dead):
            ec = BLACK
        elif dead[0]:
            ec = p2.color
        else:
            ec = p1.color

        for i in range(h):
            pygame.draw.rect(screen, ec, (0, i*dy, w*dx, dy), 0)
            for j in range(w):
                img[i][j] = ec
            for i in range(5):
                clock.tick(FPS)
                ph.set_image(center_img(img))
                pygame.display.flip()
        for i in range(120):
            clock.tick(FPS)
            for e in pygame.event.get(): pass
            for e in ph.get_all_events(): pass
            ph.set_image(center_img(img))
            pygame.display.flip()

        hh = (h+1)//2
        for i in range(hh):
            pygame.draw.rect(screen, RED, (0, (h-1-i)*dy, w*dx, dy), 0)
            for j in range(w):
                img[h-1-i][j] = RED
            pygame.draw.rect(screen, BLUE, (0, i*dy, w*dx, dy), 0)
            for j in range(w):
                img[i][j] = BLUE
            for j in range(5):
                clock.tick(FPS)
                ph.set_image(center_img(img))
                pygame.display.flip()
        while not (any([e.type == pygame.KEYDOWN
                        for e in pygame.event.get()])
                   or any([isinstance(e, KeyEvent)
                           for e in ph.get_all_events()])):
            ph.set_image(center_img(img))
            pygame.display.flip()

        reset()




    # displaying drawn images
    ph.set_image(center_img(img))
    pygame.display.flip()

    # increase loop counter / time
    t += 1
