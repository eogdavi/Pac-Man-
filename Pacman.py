"""Pac-Man em Python (pygame).

Controles: setas ou WASD para mover | ENTER reinicia | ESC sai.
"""
import math
import random
import sys

import pygame

T = 24  # tamanho do tile em pixels
HUD = 48
MAZE = [
    "###################",
    "#........#........#",
    "#o##.###.#.###.##o#",
    "#.................#",
    "#.##.#.#####.#.##.#",
    "#....#...#...#....#",
    "####.#########.####",
    "####.#       #.####",
    "####.# ##-## #.####",
    "    .  #   #  .    ",
    "####.# ##### #.####",
    "####.#       #.####",
    "####.#########.####",
    "#........#........#",
    "#.##.###.#.###.##.#",
    "#o.#..... .....#.o#",
    "##.#.#.#####.#.#.##",
    "#....#...#...#....#",
    "#.######.#.######.#",
    "#.................#",
    "###################",
]
ROWS, COLS = len(MAZE), len(MAZE[0])
WIDTH, HEIGHT = COLS * T, ROWS * T + HUD

UP, DOWN, LEFT, RIGHT = (0, -1), (0, 1), (-1, 0), (1, 0)
DIRS = [UP, LEFT, DOWN, RIGHT]
KEYS = {
    pygame.K_UP: UP, pygame.K_w: UP,
    pygame.K_DOWN: DOWN, pygame.K_s: DOWN,
    pygame.K_LEFT: LEFT, pygame.K_a: LEFT,
    pygame.K_RIGHT: RIGHT, pygame.K_d: RIGHT,
}
BLACK, BLUE, YELLOW, WHITE = (0, 0, 0), (33, 33, 222), (255, 221, 0), (255, 255, 255)

grid = []


def tile(x, y):
    if 0 <= y < ROWS:
        return grid[y][x] if 0 <= x < COLS else " "  # túnel lateral
    return "#"


def passable(x, y, door=False):
    c = tile(x, y)
    return c != "#" and (c != "-" or door)


class Mover:
    def __init__(self, tx, ty, speed):
        self.x, self.y = tx * T, ty * T
        self.dir = (0, 0)
        self.speed = self.want = speed

    def aligned(self):
        return self.x % T == 0 and self.y % T == 0

    @property
    def tx(self):
        return self.x // T

    @property
    def ty(self):
        return self.y // T

    def move(self):
        self.x += self.dir[0] * self.speed
        self.y += self.dir[1] * self.speed
        if self.x <= -T and self.dir == LEFT:
            self.x = COLS * T
        elif self.x >= COLS * T and self.dir == RIGHT:
            self.x = -T

    @property
    def center(self):
        return self.x + T // 2, self.y + T // 2 + HUD


class Pacman(Mover):
    def __init__(self):
        super().__init__(9, 15, 2)
        self.next = None
        self.face = LEFT

    def update(self):
        if self.aligned():
            if 0 <= self.tx < COLS:
                if self.next and passable(self.tx + self.next[0], self.ty + self.next[1]):
                    self.dir = self.next
                if not passable(self.tx + self.dir[0], self.ty + self.dir[1]):
                    self.dir = (0, 0)
        elif self.next == (-self.dir[0], -self.dir[1]):
            self.dir = self.next
        if self.dir != (0, 0):
            self.face = self.dir
        self.move()

    def draw(self, screen, frame):
        cx, cy = self.center
        base = math.atan2(self.face[1], self.face[0])
        mouth = abs(math.sin(frame * 0.25)) * 0.7 if self.dir != (0, 0) else 0.3
        pts = [(cx, cy)]
        steps = 20
        for i in range(steps + 1):
            a = base + mouth + (2 * math.pi - 2 * mouth) * i / steps
            pts.append((cx + math.cos(a) * (T // 2 - 2), cy + math.sin(a) * (T // 2 - 2)))
        pygame.draw.polygon(screen, YELLOW, pts)


class Ghost(Mover):
    def __init__(self, name, color, tx, ty, delay, home):
        super().__init__(tx, ty, 2)
        self.name, self.color = name, color
        self.delay, self.home = delay, home
        self.mode = "chase"  # chase | scared | eaten

    def target(self, pac, ghosts):
        px, py = pac.tx, pac.ty
        if self.name == "pinky":
            return px + 4 * pac.face[0], py + 4 * pac.face[1]
        if self.name == "inky":
            blinky = ghosts[0]
            vx, vy = px + 2 * pac.face[0], py + 2 * pac.face[1]
            return 2 * vx - blinky.tx, 2 * vy - blinky.ty
        if self.name == "clyde":
            if (px - self.tx) ** 2 + (py - self.ty) ** 2 > 64:
                return px, py
            return 0, ROWS
        return px, py

    def update(self, pac, ghosts):
        if self.delay > 0:
            self.delay -= 1
            return
        if self.aligned():
            tx, ty = self.tx, self.ty
            if self.mode == "eaten" and (tx, ty) == (9, 9):
                self.mode, self.home = "chase", True
            if self.home and ty <= 7:
                self.home = False
            self.speed = 4 if self.mode == "eaten" else (1 if self.mode == "scared" else 2)
            if 0 <= tx < COLS:
                door = self.home or self.mode == "eaten"
                opts = [d for d in DIRS if passable(tx + d[0], ty + d[1], door)]
                rev = (-self.dir[0], -self.dir[1])
                opts = [d for d in opts if d != rev] or opts
                if self.mode == "scared" or (self.mode == "chase" and not self.home and random.random() < 0.08):
                    self.dir = random.choice(opts)
                else:
                    if self.mode == "eaten":
                        goal = (9, 9)
                    elif self.home:
                        goal = (9, 7)
                    else:
                        goal = self.target(pac, ghosts)
                    self.dir = min(opts, key=lambda d: (tx + d[0] - goal[0]) ** 2 + (ty + d[1] - goal[1]) ** 2)
        self.move()

    def draw(self, screen, scared_left, frame):
        cx, cy = self.center
        if self.mode != "eaten":
            col = self.color
            if self.mode == "scared":
                flash = scared_left < 120 and (frame // 10) % 2 == 0
                col = WHITE if flash else BLUE
            r = T // 2 - 2
            pygame.draw.circle(screen, col, (cx, cy - 2), r)
            pygame.draw.rect(screen, col, (cx - r, cy - 2, 2 * r, r))
            for i in range(4):  # "saia" ondulada
                off = 2 if (i + frame // 8) % 2 else 0
                pygame.draw.circle(screen, col, (cx - r + r // 4 + i * r // 2, cy + r - 2 + off), r // 4 + 1)
        if self.mode == "scared":
            pygame.draw.circle(screen, WHITE, (cx - 4, cy - 3), 2)
            pygame.draw.circle(screen, WHITE, (cx + 4, cy - 3), 2)
        else:
            for ex in (-4, 4):
                pygame.draw.circle(screen, WHITE, (cx + ex, cy - 3), 4)
                pygame.draw.circle(screen, (20, 20, 200), (cx + ex + self.dir[0] * 2, cy - 3 + self.dir[1] * 2), 2)


class Game:
    def __init__(self):
        self.high = 0
        self.new()

    def new(self):
        global grid
        grid = [list(r) for r in MAZE]
        self.score, self.lives, self.frame = 0, 3, 0
        self.pellets = sum(r.count(".") + r.count("o") for r in MAZE)
        self.spawn()

    def spawn(self):
        self.pac = Pacman()
        self.ghosts = [
            Ghost("blinky", (255, 0, 0), 9, 7, 0, False),
            Ghost("pinky", (255, 184, 255), 9, 9, 120, True),
            Ghost("inky", (0, 255, 255), 8, 9, 240, True),
            Ghost("clyde", (255, 184, 82), 10, 9, 360, True),
        ]
        self.scared, self.combo = 0, 200
        self.state, self.timer = "ready", 120

    def eat(self):
        if not (self.pac.aligned() and 0 <= self.pac.tx < COLS):
            return
        x, y = self.pac.tx, self.pac.ty
        c = grid[y][x]
        if c in ".o":
            grid[y][x] = " "
            self.pellets -= 1
            self.score += 10 if c == "." else 50
            if c == "o":
                self.scared, self.combo = 60 * 7, 200
                for g in self.ghosts:
                    if g.mode == "chase" and g.delay == 0:
                        g.mode = "scared"
                        g.dir = (-g.dir[0], -g.dir[1])
        self.high = max(self.high, self.score)

    def update(self):
        self.frame += 1
        if self.state == "ready":
            self.timer -= 1
            if self.timer <= 0:
                self.state = "play"
            return
        if self.state != "play":
            return
        self.pac.update()
        self.eat()
        if self.pellets == 0:
            self.state = "win"
            return
        for g in self.ghosts:
            g.update(self.pac, self.ghosts)
        if self.scared:
            self.scared -= 1
            if self.scared == 0:
                for g in self.ghosts:
                    if g.mode == "scared":
                        g.mode = "chase"
        for g in self.ghosts:
            if math.hypot(g.x - self.pac.x, g.y - self.pac.y) < T * 0.65:
                if g.mode == "scared":
                    g.mode = "eaten"
                    self.score += self.combo
                    self.combo *= 2
                elif g.mode == "chase":
                    self.lives -= 1
                    if self.lives == 0:
                        self.state = "over"
                    else:
                        self.spawn()
                    return

    def draw(self, screen, font, big):
        screen.fill(BLACK)
        for y, row in enumerate(grid):
            for x, c in enumerate(row):
                px, py = x * T, y * T + HUD
                if c == "#":
                    pygame.draw.rect(screen, BLUE, (px + 3, py + 3, T - 6, T - 6), 2, border_radius=5)
                elif c == "-":
                    pygame.draw.line(screen, (255, 184, 255), (px, py + T // 2), (px + T, py + T // 2), 3)
                elif c == ".":
                    pygame.draw.circle(screen, (255, 210, 170), (px + T // 2, py + T // 2), 3)
                elif c == "o" and (self.frame // 15) % 2 == 0:
                    pygame.draw.circle(screen, (255, 210, 170), (px + T // 2, py + T // 2), 8)
        self.pac.draw(screen, self.frame)
        for g in self.ghosts:
            g.draw(screen, self.scared, self.frame)
        screen.blit(font.render(f"PONTOS {self.score}", True, WHITE), (10, 8))
        screen.blit(font.render(f"RECORDE {self.high}", True, YELLOW), (10, 28))
        for i in range(self.lives):
            pygame.draw.circle(screen, YELLOW, (WIDTH - 20 - i * 24, 24), 9)
        msg = {"ready": "PRONTO!", "over": "FIM DE JOGO - ENTER", "win": "VOCÊ VENCEU! - ENTER"}.get(self.state)
        if msg:
            txt = big.render(msg, True, YELLOW)
            rect = txt.get_rect(center=(WIDTH // 2, 11 * T + HUD + T // 2))
            pygame.draw.rect(screen, BLACK, rect.inflate(16, 8))
            screen.blit(txt, rect)


def main():
    pygame.init()
    pygame.display.set_caption("Pac-Man em Python")
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    font, big = pygame.font.Font(None, 22), pygame.font.Font(None, 30)
    game = Game()
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT or (e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE):
                pygame.quit()
                sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key in KEYS:
                    game.pac.next = KEYS[e.key]
                elif e.key == pygame.K_RETURN and game.state in ("over", "win"):
                    game.new()
        game.update()
        game.draw(screen, font, big)
        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()
  
