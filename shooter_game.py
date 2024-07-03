import pygame
import math

# Initialisation de Pygame
pygame.init()

# Définir les couleurs
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (169, 169, 169)

# Définir les dimensions de la fenêtre
WIDTH, HEIGHT = 800, 600
BANNER_HEIGHT = 40
screen = pygame.display.set_mode((WIDTH, HEIGHT + BANNER_HEIGHT))
pygame.display.set_caption("Jeu de disques")

# Définir l'obstacle central
obstacle_radius = min(WIDTH, HEIGHT) // 3 // 2
obstacle_x = WIDTH // 2
obstacle_y = HEIGHT // 2

# Définir la classe Joueur
class Player:
    def __init__(self, x, y, angle, color, controls):
        self.x = x
        self.y = y
        self.color = color
        self.controls = controls
        self.angle = angle
        self.radius = 20
        self.speed = 5
        self.health = 5
        self.max_health = 5
        self.shield = True
        self.shield_timer = 0
        self.last_shot_time = 0
        self.deaths = 0
        self.respawn_timer = 0
        self.invincible = False
        self.attached = True  # Les joueurs commencent accrochés
        self.ejection_power = 0
        self.max_ejection_power = 15
        self.ejection_start_time = 0
        self.vx = 0
        self.vy = 0
        self.attached_to_obstacle = True  # Commence collé à l'obstacle

    def draw(self):
        # Dessiner le joueur
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y) + BANNER_HEIGHT), self.radius)
        # Dessiner le trait directionnel
        end_x = self.x + math.cos(self.angle) * (self.radius + 10)
        end_y = self.y + math.sin(self.angle) * (self.radius + 10)
        pygame.draw.line(screen, self.color, (self.x, self.y + BANNER_HEIGHT), (end_x, end_y + BANNER_HEIGHT), 5)

        # Dessiner la barre de vie
        health_bar_length = self.radius * 2
        health_ratio = self.health / self.max_health
        pygame.draw.rect(screen, RED, (self.x - self.radius, self.y - self.radius - 10 + BANNER_HEIGHT, health_bar_length, 5))
        pygame.draw.rect(screen, GREEN, (self.x - self.radius, self.y - self.radius - 10 + BANNER_HEIGHT, health_bar_length * health_ratio, 5))

    def update(self, keys, current_time):
        # Mettre à jour la direction en fonction de l'effet de recul
        if keys[self.controls['left']]:
            self.angle -= 0.1
        if keys[self.controls['right']]:
            self.angle += 0.1

        # Gérer l'inertie uniquement si le joueur n'est pas collé à un obstacle
        if not self.attached_to_obstacle:
            if keys[self.controls['down']]:
                # Accrochage à l'obstacle si proche
                if self.check_proximity_to_obstacle():
                    self.attached_to_obstacle = True
                    self.vx = 0
                    self.vy = 0
            else:
                # Si l'utilisateur lâche la touche, détacher immédiatement
                self.attached_to_obstacle = False

            if not self.attached_to_obstacle:
                self.x += self.vx
                self.y += self.vy

                # Gérer les bords de l'écran (espace cyclique)
                self.x %= WIDTH
                self.y %= HEIGHT
        else:
            # Si collé à l'obstacle, rester immobile
            self.vx = 0
            self.vy = 0

    def take_damage(self):
        if not self.invincible:
            self.health -= 1
            if self.health <= 0:
                self.deaths += 1
                self.invincible = True
                self.respawn_timer = pygame.time.get_ticks()

    def check_proximity_to_obstacle(self):
        distance = math.hypot(self.x - obstacle_x, self.y - obstacle_y)
        return distance < self.radius + obstacle_radius
    
    def check_collision_with_obstacle(self):
        distance = math.hypot(self.x - obstacle_x, self.y - obstacle_y)
        if distance < self.radius + obstacle_radius:
            # Calculer l'angle entre le joueur et l'obstacle
            angle_to_obstacle = math.atan2(self.y - obstacle_y, self.x - obstacle_x)
            # Calculer la nouvelle direction en rebondissant sur l'obstacle
            new_angle = 2 * angle_to_obstacle - self.angle + math.pi
            self.angle = new_angle
            # Mettre à jour la vitesse en fonction de la nouvelle direction
            self.vx = math.cos(self.angle) * self.speed
            self.vy = math.sin(self.angle) * self.speed
            # Réajuster la position pour ne pas rester coincé dans l'obstacle
            self.x += self.vx
            self.y += self.vy

# Initialiser les joueurs aux bords opposés de l'obstacle central
player1 = Player(obstacle_x + obstacle_radius + 30, obstacle_y, math.pi, RED, {'left': pygame.K_LEFT, 'right': pygame.K_RIGHT, 'forward': pygame.K_UP, 'shoot': pygame.K_UP, 'down': pygame.K_DOWN})
player2 = Player(obstacle_x - obstacle_radius - 30, obstacle_y, 0, GREEN, {'left': pygame.K_q, 'right': pygame.K_d, 'forward': pygame.K_z, 'shoot': pygame.K_z, 'down': pygame.K_s})

# Liste pour les tirs
bullets = []

# Classe pour les tirs
class Bullet:
    def __init__(self, x, y, angle, color):
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = 2.5  # Nouvelle vitesse réduite
        self.color = color
        self.creation_time = pygame.time.get_ticks()

    def update(self):
        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed
        self.x %= WIDTH
        self.y %= HEIGHT

    def draw(self):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y) + BANNER_HEIGHT), 5)
        
    def check_collision(self, player):
        distance = math.hypot(self.x - player.x, self.y - player.y)
        return distance < player.radius

    def should_delete(self, current_time):
        return current_time - self.creation_time > 10000  # Supprimer après 10 secondes

def shoot_bullet(player):
    bullet_x = player.x + math.cos(player.angle) * (player.radius + 5)
    bullet_y = player.y + math.sin(player.angle) * (player.radius + 5)
    bullets.append(Bullet(bullet_x, bullet_y, player.angle, player.color))
    # Appliquer l'effet de recul
    player.vx -= math.cos(player.angle) * 0.5
    player.vy -= math.sin(player.angle) * 0.5

# Boucle principale du jeu
running = True
clock = pygame.time.Clock()

while running:
    screen.fill(BLACK)
    keys = pygame.key.get_pressed()
    current_time = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Dessiner le bandeau supérieur
    pygame.draw.rect(screen, GRAY, (0, 0, WIDTH, BANNER_HEIGHT))
    font = pygame.font.Font(None, 36)
    death_text1 = font.render(f"Player 1 Deaths: {player1.deaths}", True, BLACK)
    death_text2 = font.render(f"Player 2 Deaths: {player2.deaths}", True, BLACK)
    screen.blit(death_text1, (10, 5))
    screen.blit(death_text2, (10, 5 + death_text1.get_height()))

    # Dessiner l'obstacle
    pygame.draw.circle(screen, BLUE, (obstacle_x, obstacle_y + BANNER_HEIGHT), obstacle_radius)

    # Mettre à jour et dessiner les joueurs
    player1.update(keys, current_time)
    player2.update(keys, current_time)
    player1.check_collision_with_obstacle()
    player2.check_collision_with_obstacle()
    player1.draw()
    player2.draw()

    # Tirer des balles pour player1
    if keys[player1.controls['shoot']] and current_time - player1.last_shot_time > 1000 and not player1.invincible:
        shoot_bullet(player1)
        player1.last_shot_time = current_time
    
    # Tirer des balles pour player2
    if keys[player2.controls['shoot']] and current_time - player2.last_shot_time > 1000 and not player2.invincible:
        shoot_bullet(player2)
        player2.last_shot_time = current_time

    # Mettre à jour et dessiner les balles
    for bullet in bullets[:]:
        bullet.update()
        bullet.draw()
        if bullet.should_delete(current_time):
            bullets.remove(bullet)
        elif bullet.check_collision(player1):
            bullets.remove(bullet)
            player1.take_damage()
        elif bullet.check_collision(player2):
            bullets.remove(bullet)
            player2.take_damage()

    pygame.display.flip()
    clock.tick()
