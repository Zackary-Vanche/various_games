import pygame
import pygame.locals
import numpy as np
import math
import random
import time
from colorsys import hls_to_rgb
from perlin_noise import perlin_noise
from scipy.ndimage import zoom

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
GRAY = (169, 169, 169)
TRAJ_COLOR = WHITE

# Définir les dimensions de la fenêtre
WIDTH, HEIGHT = 1500, 750
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Golf")

f = 1
g = 5000*f  # Constante de gravité
vinitmax = 3*f # vitesse maximale
vdiv = 75/vinitmax
dt = 0.75
coeff=2
zoom_factor = 75
scale = 5
friction = 1-5e-2

def calculate_gradient(matrix, i, j):
    m, n = matrix.shape
    di, dj = 0, 0

    # Partial derivative with respect to i
    if 0 < i < m-1:
        di = (matrix[i+1, j] - matrix[i-1, j]) / 2
    elif i == 0:
        di = matrix[i+1, j] - matrix[i, j]
    elif i == m-1:
        di = matrix[i, j] - matrix[i-1, j]

    # Partial derivative with respect to j
    if 0 < j < n-1:
        dj = (matrix[i, j+1] - matrix[i, j-1]) / 2
    elif j == 0:
        dj = matrix[i, j+1] - matrix[i, j]
    elif j == n-1:
        dj = matrix[i, j] - matrix[i, j-1]

    return np.array([di, dj])

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
        bullet_x = self.x + (self.radius + 20) * vx / np.linalg.norm(v)
        bullet_y = self.y + (self.radius + 20) * vy / np.linalg.norm(v)
        return Bullet(bullet_x, bullet_y, vx, vy, self, self.color, click_pos)

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
        self.n_moves = 0
        
    def update(self, altitude_matrix):
        # Mettre à jour la position de la balle en fonction de son angle et de sa vitesse
        ax, ay = calculate_gradient(altitude_matrix, int(self.y), int(self.x))
        vx = self.vx*dt + g*ax*dt**2/2
        vy = self.vy*dt + g*ay*dt**2/2
        vx = vx*friction
        vy = vy*friction
        v = np.linalg.norm([vx, vy])
        for i in range(1, 2+1, 1):
            if v <= i:
                #vx = vx*(1+np.random.random()/2)
                #vy = vy*(1+np.random.random()/2)
                self.vx = self.vx*1.01
                self.vy = self.vy*1.01
        vx = self.vx*dt + g*ax*dt**2/2
        vy = self.vy*dt + g*ay*dt**2/2
        vx = vx*friction
        vy = vy*friction
        self.x = self.x + vx
        self.y = self.y + vy
        self.traj.append((self.x, self.y))
        self.n_moves += 1

    def draw(self):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), 3)
        if len(bullet.traj) > 1:
            pygame.draw.lines(screen, TRAJ_COLOR, False, bullet.traj, 1)

    def check_collision(self, circle):
        distance = math.hypot(self.x - circle.x, self.y - circle.y)
        return distance < circle.radius
    
# Champ de hauteur

# Générer le bruit de Perlin

def get_altitude_color(altitude_matrix):
    # Conversion de la matrice en couleurs HSV
    # Ajustement de la luminosité proportionnelle aux valeurs de la matrice
    v = (altitude_matrix * 255).astype(np.uint8)
    # Création de l'image colorée en RVB à partir des valeurs HSV
    image = np.zeros((WIDTH, HEIGHT, 3), dtype=np.uint8)
    hue_degraded = 1#♣np.random.random() < 0.2
    for y in range(WIDTH):
        for x in range(HEIGHT):
            hue = (1 - altitude_matrix[x, y]) * 10  # Convertir de 270° (bleu/violet) à 0° (rouge)
            r, g, b = hls_to_rgb(hue, abs(altitude_matrix[x, y]*0.5), 0.9)
            image[y, x, 0] = int(r * 255)
            image[y, x, 1] = int(g * 255)
            image[y, x, 2] = int(b * 255)
    return image

altitude_matrix = zoom(perlin_noise(WIDTH//zoom_factor, HEIGHT//zoom_factor, scale=scale), zoom_factor)
image = get_altitude_color(altitude_matrix)

# Initialisation des joueurs 

nx = 5
ny = 3
player_radius = 15
player0 = Player(x=WIDTH // nx,
                 y=HEIGHT // ny,
                 radius=player_radius,
                 color=WHITE)
player1 = Player(x=WIDTH * (nx-1) // nx,
                 y=HEIGHT * (ny-1) // ny,
                 radius=player_radius,
                 color=WHITE)
players_list = [player0, player1]

def dist(x1, y1, x2, y2):
    return np.sqrt((x1-x2)**2+(y1-y2)**2)

# Boucle principale du jeu
running = True
clock = pygame.time.Clock()

who_plays = 0

bullets_list = []
bullet_traj_list = []
old_crosses = []
n_test = 0

while running:
    screen.blit(pygame.surfarray.make_surface(image), (0, 0))
    WIDTH, HEIGHT = screen.get_size()
    keys = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN and len(bullets_list) == 0:
            vinitmax = vinitmax*1.05
            for i in range(len(bullet_traj_list)):
                bullet_traj_list[i]['color'] = np.array(bullet_traj_list[i]['color'])*0.95
            mouse_x, mouse_y = event.pos
            shooter = players_list[who_plays]
            d = dist(x1=shooter.x, y1=shooter.y, x2=mouse_x, y2=mouse_y) - shooter.radius
            # Additive
            h = 0.5
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
    
    for bullet in bullets_list:
        bullet.draw()
        if bullet.x < 0 or bullet.y < 0 or bullet.x > WIDTH or bullet.y > HEIGHT:
            bullets_list.remove(bullet)
            bullet_traj_list.append({"traj":bullet.traj,
                                     "pos":bullet.click_pos,
                                     "color":TRAJ_COLOR})
                
    for traj_pos in bullet_traj_list:
        traj = traj_pos['traj']
        pos = traj_pos['pos']
        color = traj_pos["color"]
        if len(traj) > 1:
            # Trajectoire
            line_width = 1
            if np.linalg.norm(color) > 200:
                line_width = 1
            if np.linalg.norm(color) > 100:
                pygame.draw.lines(screen, color, False, traj, line_width)
                # Croix
                cross_center = pos
                cross_size = 5
                horizontal_start = (cross_center[0] - cross_size, cross_center[1])
                horizontal_end = (cross_center[0] + cross_size, cross_center[1])
                vertical_start = (cross_center[0], cross_center[1] - cross_size)
                vertical_end = (cross_center[0], cross_center[1] + cross_size)
                pygame.draw.line(screen, BLACK, horizontal_start, horizontal_end, 3)
                pygame.draw.line(screen, BLACK, vertical_start, vertical_end, 3)
                pygame.draw.line(screen, WHITE, horizontal_start, horizontal_end, 1)
                pygame.draw.line(screen, WHITE, vertical_start, vertical_end, 1)
            
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
        pygame.draw.circle(screen, RED, (int(player0.x), int(player0.y)), 2*player0.radius//3-2)
        pygame.draw.circle(screen, BLACK, (int(player1.x), int(player1.y)), 2*player1.radius//3-2)
    else:
        pygame.draw.circle(screen, BLACK, (int(player1.x), int(player1.y)), 2*player1.radius//3+2)
        pygame.draw.circle(screen, RED, (int(player1.x), int(player1.y)), 2*player1.radius//3-2)
        pygame.draw.circle(screen, BLACK, (int(player0.x), int(player0.y)), 2*player0.radius//3-2)

    # Mettre à jour et dessiner les balles des joueurs
    collision_player_0 = False
    collision_player_1 = False
    for bullet in bullets_list:
        if 0 < bullet.x < WIDTH and 0 < bullet.y < HEIGHT:
            bullet.update(altitude_matrix)
        else:
            bullets_list.remove(bullet)
            bullet_traj_list.append({"traj":bullet.traj,
                                     "pos":bullet.click_pos,
                                     "color":TRAJ_COLOR})
        if bullet.n_moves > 1000 or np.linalg.norm(np.array([bullet.vx, bullet.vy])) < 0.1:
            bullets_list.remove(bullet)
            bullet_traj_list.append({"traj":bullet.traj,
                                     "pos":bullet.click_pos,
                                     "color":TRAJ_COLOR})
        if len(bullet.traj) > 100:
            if dist(bullet.traj[-100][0], bullet.traj[-100][1],
                    bullet.traj[-1][0], bullet.traj[-1][1]) < 10:
                bullets_list.remove(bullet)
                bullet_traj_list.append({"traj":bullet.traj,
                                         "pos":bullet.click_pos,
                                         "color":TRAJ_COLOR})
        if len(bullet.traj) > 200:
            if dist(bullet.traj[-200][0], bullet.traj[-200][1],
                    bullet.traj[-1][0], bullet.traj[-1][1]) < 25:
                bullets_list.remove(bullet)
                bullet_traj_list.append({"traj":bullet.traj,
                                         "pos":bullet.click_pos,
                                         "color":TRAJ_COLOR})
        bullet.draw()
        if bullet.check_collision(player1):
            collision_player_1 = True
        if bullet.check_collision(player0):
            collision_player_0 = True
    if collision_player_0 or collision_player_1:
        vinitmax = 3*f
        bullet_traj_list = []
        bullets_list = []
        n_test = 0
        altitude_matrix = zoom(perlin_noise(WIDTH//zoom_factor, HEIGHT//zoom_factor, scale=scale), zoom_factor)
        image = get_altitude_color(altitude_matrix)
    if collision_player_0:
        player1.score += 1
        who_plays = 0
    if collision_player_1:
        player0.score += 1
        who_plays = 1
        
    pygame.display.flip()
    clock.tick(60)
    
    if keys[pygame.locals.K_ESCAPE]:
        pygame.quit()
    
    time.sleep(0.0001)

pygame.quit()
