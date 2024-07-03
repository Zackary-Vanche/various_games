import pygame
import pygame.locals
import numpy as np
import math
import random
import time
from colorsys import hls_to_rgb

pygame.init()

# Définir les couleurs
WHITE = (255, 255, 255)
GREY = (127, 127, 127)
BLACK = (0, 0, 0)
DARK_BLUE = (30, 30, 125)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PLANET_COLOR = (200, 160, 160)
YELLOW = (255, 255, 0)
GRAY = (169, 169, 169)

def PLANET_COLOR():
    hu = np.random.random()
    return np.array(255*np.array(hls_to_rgb(hu, 0.85, 0.7)), dtype=np.uint8).tolist()

# Définir les dimensions de la fenêtre
WIDTH, HEIGHT = 1500, 780
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Slingshot")

f = 1
g = 250*f  # Constante de gravité
vmin = 2 # vitesse minimale
vinitmax = 15*f # vitesse maximale
amax_planet = 30*f # accélération maximale
astep_planet = 1
vdiv = 250/vinitmax
dt = 0.5
num_planets = 10
coeff=2

# Classe pour les objets gravitationnels (joueurs et planètes)
class RoundObject:
    def __init__(self, x, y, radius, color):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color

    def draw(self):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)

# Classe pour les joueurs
class Player(RoundObject):
    def __init__(self, x, y, radius, color):
        super().__init__(x, y, radius, color)
        self.score = 0
        self.vx = 0  # Vitesse horizontale initiale
        self.vy = 0  # Vitesse verticale initiale
        self.missed_shots = []  # Liste des tirs manqués
        self.last_shot_time = 0  # Temps du dernier tir

    def rotate_left(self):
        self.angle -= math.radians(5)

    def rotate_right(self):
        self.angle += math.radians(5)

    def shoot(self, vx, vy, click_pos):
        # Créer un tir à partir de la position actuelle du joueur
        v = np.array([vx, vy])
        bullet_x = self.x + (self.radius + 10) * vx / np.linalg.norm(v)
        bullet_y = self.y + (self.radius + 10) * vy / np.linalg.norm(v)
        return Bullet(bullet_x, bullet_y, vx, vy, self, self.color, click_pos)

# Classe pour les planètes
class Planet(RoundObject):
    def __init__(self, x, y, radius, color):
        super().__init__(x, y, radius, color)
        self.weight = np.pi * self.radius**2

# Classe pour les balles
class Bullet:
    def __init__(self, x, y, vx, vy, player, color, click_pos):
        self.x = x
        self.y = y
        v = np.linalg.norm([vx, vy])
        if v > vinitmax:
            vx = vinitmax*vx/v
            vy = vinitmax*vy/v
        self.vx = vx
        self.vy = vy
        self.player = player
        self.color = color
        self.traj = [(self.x, self.y)]
        self.click_pos = click_pos
        
    def update(self, planets_list):
        # Mettre à jour la position de la balle en fonction de son angle et de sa vitesse
        ax, ay = get_acceleraction(self.x, self.y, planets_list)
        vx = self.vx*dt + ax*dt**2/2
        vy = self.vy*dt + ay*dt**2/2
        v = np.linalg.norm([vx, vy])
        if v < vmin:
            vx = vmin*vx/v
            vy = vmin*vy/v
        a = np.linalg.norm([ax, ay])
        self.x = self.x + vx
        self.y = self.y + vy
        self.traj.append((self.x, self.y))

    def draw(self):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), 3)
        if len(bullet.traj) > 1:
            pygame.draw.lines(screen, YELLOW, False, bullet.traj, 1)

    def check_collision(self, circle):
        distance = math.hypot(self.x - circle.x, self.y - circle.y)
        return distance < circle.radius
    
def stair(a, astep):
    return (a//astep_planet)*astep_planet
    
def get_acceleraction(x, y, planets_list):
    ax = 0
    ay = 0
    for planet in planets_list:
        d = np.linalg.norm([x-planet.x,
                            y-planet.y])
        ax += (planet.x-x) * planet.weight / d**(coeff+1) * g
        ay += (planet.y-y) * planet.weight / d**(coeff+1) * g
        a = np.linalg.norm(np.array([ax, ay]))
        if a > amax_planet:
            ax = amax_planet*ax/a
            ay = amax_planet*ay/a
        #a_new = stair(a, astep_planet)
        #assert a_new <= a
        #assert abs(a_new*ax/a) <= abs(ax)
        #assert abs(a_new*ay/a) <= abs(ay)
        #ax = a_new*ax/a
        #ay = a_new*ay/a
    return ax, ay

# Initialisation des joueurs et des planètes
nx = 5
ny = 3
player_radius = 20
player0 = Player(x=WIDTH // nx,
                 y=HEIGHT // ny,
                 radius=player_radius,
                 color=RED)
player1 = Player(x=WIDTH * (nx-1) // nx,
                 y=HEIGHT * (ny-1) // ny,
                 radius=player_radius,
                 color=GREEN)
players_list = [player0, player1]
planets_list = []


def dist(x1, y1, x2, y2):
    return np.sqrt((x1-x2)**2+(y1-y2)**2)

def initialize_planets():
    global planets_list
    planets_list = []
    planets_list = [Planet(WIDTH//2+random.randint(-30, 30),
                           HEIGHT//2+random.randint(-30, 30),
                           30,
                           PLANET_COLOR())]
    while len(planets_list) < num_planets:
        radius = random.randint(20, 40)
        fact = 1.5
        x = random.randint(int(fact*radius), int(WIDTH-fact*radius))
        y = random.randint(int(fact*radius), int(HEIGHT-fact*radius))
        intersection = False
        for player in players_list:
            if dist(x, y, player.x, player.y) < 2*radius + player.radius + 40:
                intersection = True
        for planet in planets_list:
            if dist(x, y, planet.x, planet.y) < 2*radius + 2*planet.radius + 10:
                intersection = True
        if not intersection:
            color = PLANET_COLOR()
            planet = Planet(x, y, radius, color)
            planets_list.append(planet)
    planets_list[1:] = sorted(planets_list[1:], key=lambda planet : planet.weight)
    #planets_list = sorted(planets_list, key=lambda planet : planet.weight)
    planets_list.reverse()
    assert len(planets_list) == num_planets
initialize_planets()

# Boucle principale du jeu
running = True
clock = pygame.time.Clock()

who_plays = 0

bullets_list = []
bullet_traj_list = []
old_crosses = []
n_test = 0
n_test_k = 0

while running:
    screen.fill(BLACK)
    WIDTH, HEIGHT = screen.get_size()
    keys = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN and len(bullets_list) == 0:
            mouse_x, mouse_y = event.pos
            shooter = players_list[who_plays]
            d = dist(x1=shooter.x, y1=shooter.y, x2=mouse_x, y2=mouse_y) - shooter.radius
            # Additive
            h = 0.25
            l = np.arange(-h, 2*h, h)
            vxvy_list = []
            for i in l:
                for j in l:
                    vx=mouse_x-shooter.x
                    vy=mouse_y-shooter.y
                    vx = vx+i
                    vy = vy+j
                    vxvy_list.append((vx+i, vy+j))
                    assert not np.isnan(vx)
                    assert not np.isnan(vy)
            # Multiplicative
            """
            h = 0.05
            np.arange(1-h, 1+2*h, h)
            vxvy_list = []
            for i in l:
                for j in l:
                    vx=mouse_x-shooter.x
                    vy=mouse_y-shooter.y
                    vx = vx*i
                    vy = vy*j
                    vxvy_list.append((vx, vy))
                    assert not np.isnan(vx)
                    assert not np.isnan(vy)
            """
            for vxvy in vxvy_list:
                vx, vy = vxvy
                bullet = shooter.shoot(vx=vx/vdiv, vy=vy/vdiv, click_pos=event.pos)
                bullets_list.append(bullet)
            who_plays = (who_plays+1)%2
            n_test += 1
    
    WIDTH, HEIGHT
    for i in range(0, WIDTH, 20):
        pygame.draw.lines(screen, DARK_BLUE, False, [(i, 0), (i, HEIGHT)], 1)
    for i in range(0, HEIGHT, 20):
        pygame.draw.lines(screen, DARK_BLUE, False, [(0, i), (WIDTH, i)], 1)
    
    for planet in planets_list:
        planet.draw()

    for bullet in bullets_list:
        bullet.draw()
        if bullet.x < 0 or bullet.y < 0 or bullet.x > WIDTH or bullet.y > HEIGHT:
            bullets_list.remove(bullet)
            bullet_traj_list.append({"traj":bullet.traj,
                                     "pos":bullet.click_pos,
                                     "color":bullet.color})
                
    for traj_pos in bullet_traj_list:
        traj = traj_pos['traj']
        pos = traj_pos['pos']
        color = traj_pos["color"]
        if len(traj) > 1:
            # Trajectoire
            line_width = 1
            cross_color = GREY
            if np.linalg.norm(color) > 200:
                line_width = 1
                cross_color = WHITE
            if np.linalg.norm(color) > 100:
                pygame.draw.lines(screen, color, False, traj, line_width)
                # Croix
                cross_center = pos
                cross_size = 5
                horizontal_start = (cross_center[0] - cross_size, cross_center[1])
                horizontal_end = (cross_center[0] + cross_size, cross_center[1])
                vertical_start = (cross_center[0], cross_center[1] - cross_size)
                vertical_end = (cross_center[0], cross_center[1] + cross_size)
                pygame.draw.line(screen, cross_color, horizontal_start, horizontal_end, 2)
                pygame.draw.line(screen, cross_color, vertical_start, vertical_end, 2)
            
    # Définir le texte à afficher
    text = f"{player0.score} | {player1.score}"
    font_size = 36
    # Créer une police
    font = pygame.font.Font(None, font_size)  # Utiliser None pour la police par défaut
    # Rendre le texte
    text_surface = font.render(text, True, (255, 255, 255))
    screen.blit(text_surface, (10, 10))  # Position (10, 10)

    player0.draw()
    player1.draw()
    
    rectangle0 = pygame.Rect(player0.x-vdiv*vinitmax,
                             player0.y-vdiv*vinitmax,
                             2*vdiv*vinitmax,
                             2*vdiv*vinitmax)
    pygame.draw.ellipse(screen,
                        player0.color,
                        rectangle0,
                        width=1)
    rectangle1 = pygame.Rect(player1.x-vdiv*vinitmax,
                             player1.y-vdiv*vinitmax,
                             2*vdiv*vinitmax,
                             2*vdiv*vinitmax)
    pygame.draw.ellipse(screen,
                        player1.color,
                        rectangle1,
                        width=1)
    
    if who_plays == 0:
        pygame.draw.circle(screen, BLACK, (int(player0.x), int(player0.y)), 2*player0.radius//3+2)
        pygame.draw.circle(screen, YELLOW, (int(player0.x), int(player0.y)), 2*player0.radius//3-2)
    else:
        pygame.draw.circle(screen, BLACK, (int(player1.x), int(player1.y)), 2*player1.radius//3+2)
        pygame.draw.circle(screen, YELLOW, (int(player1.x), int(player1.y)), 2*player1.radius//3-2)

    # Mettre à jour et dessiner les balles des joueurs
    collision_player_0 = False
    collision_player_1 = False
    for bullet in bullets_list:
        bullet.update(planets_list)
        for planet in planets_list:
            if bullet.check_collision(planet) and planet.weight != 0:
                bullets_list.remove(bullet)
                bullet_traj_list.append({"traj":bullet.traj,
                                         "pos":bullet.click_pos,
                                         "color":bullet.color})
        bullet.draw()
        if bullet.check_collision(player1):
            collision_player_1 = True
        if bullet.check_collision(player0):
            collision_player_0 = True
    if collision_player_0 or collision_player_1:
        initialize_planets()
        bullet_traj_list = []
        bullets_list = []
        time.sleep(3)
        n_test = 0
        n_test_k = 0
    if collision_player_0:
        player1.score += 1
        who_plays = 0
    if collision_player_1:
        player0.score += 1
        who_plays = 1
    
    k = 6
    # n_test != 0 and n_test%k == 0 and n_test//k-1==n_test_k
    if (n_test_k+1)*k<n_test+1 and len(bullets_list)==0:
        planets_list[n_test//k-1].weight = 0
        planets_list[n_test//k-1].color = (40, 40, 40)
        for i in range(len(bullet_traj_list)):
            bullet_traj_list[i]['color'] = np.array(bullet_traj_list[i]['color'])/2
        n_test_k += 1
        #if len(bullet_traj_list) == k:
        
    pygame.display.flip()
    clock.tick(60)
    
    if keys[pygame.locals.K_ESCAPE]:
        pygame.quit()
    
    time.sleep(0.0001)

pygame.quit()
