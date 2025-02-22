import pygame
import random
import math
import sys

pygame.init()

# Screen
WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Invaders")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
PURPLE = (128, 0, 128)

# Game States
MENU = "menu"
PLAYING = "playing"
PAUSED = "paused"
GAME_OVER = "game_over"

# Fonts
default_font = pygame.font.Font(None, 36)

# Player 
class Player:
    def __init__(self):
        self.width = 50
        self.height = 40
        self.x = WIDTH // 2 - self.width // 2
        self.y = HEIGHT - 60
        self.color = GREEN
        self.base_speed = 5
        self.speed = self.base_speed
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.base_max_bullets = 2
        self.max_bullets = self.base_max_bullets
        self.speed_timer = 0
        self.bullet_timer = 0

    # Player movement
    def move(self, dx, dy):

        # x movement
        self.x += dx
        if self.x < 0:
            self.x = 0
        elif self.x > WIDTH - self.width:
            self.x = WIDTH - self.width

        # y movement
        self.y += dy
        if self.y < 0:
            self.y = 0
        elif self.y > HEIGHT - self.height:
            self.y = HEIGHT - self.height

        self.rect.topleft = (self.x, self.y)

    def update_timers(self):
        if self.speed_timer > 0:
            self.speed_timer -= 1
            if self.speed_timer <= 0:
                self.speed = self.base_speed
        
        if self.bullet_timer > 0:
            self.bullet_timer -= 1
            if self.bullet_timer <= 0:
                self.max_bullets = self.base_max_bullets

    def draw(self):
        pygame.draw.rect(screen, GREEN, self.rect)

# Enemies
class Enemy:
    def __init__(self, x, y, type_="normal"):
        self.width = 40
        self.height = 30
        self.x = x
        self.y = y
        self.type = type_
        self.speed = 2
        self.health = 1 if type_ != "normal" else 2
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.shoot_timer = random.randint(60, 180)  # Shots every 1-3 seconds
        self.sine_offset = random.uniform(0, 2 * math.pi)

    def move(self, frame_count):
        if self.type == "normal":
            self.x += self.speed
        elif self.type == "sine":
            self.x += self.speed
            self.y = 50 + math.sin(frame_count * 0.05 + self.sine_offset) * 50
        self.rect.topleft = (self.x, self.y)

    def draw(self):
        color = YELLOW if self.type == "sine" else RED
        pygame.draw.rect(screen, color, self.rect)

# Bullets
class Bullet:
    def __init__(self, x, y, angle=0, speed=-10):
        self.width = 5
        self.height = 15
        self.x = x
        self.y = y
        self.speed = speed
        self.angle = angle
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def move(self):
        self.y += self.speed * math.cos(math.radians(self.angle))
        self.x += self.speed * math.sin(math.radians(self.angle))
        self.rect.topleft = (self.x, self.y)

    def draw(self):
        pygame.draw.rect(screen, YELLOW if self.speed < 0 else RED, self.rect)

# Boss
class Boss:
    def __init__(self, round_num):
        self.width = 100
        self.height = 80
        self.x = WIDTH // 2 - self.width // 2
        self.y = 50
        self.speed = 3
        # Health, starts at 100 and goes up by 25% every 5 rounds
        self.health = int(100 * (1.25 ** ((round_num // 5) - 1))) if round_num >= 5 else 100
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.shoot_timer = random.randint(60, 120)  # Shots every 1-2 seconds
        self.attack_type = 0
        self.special_timer = 300
        self.spawn_timer = 600

    def move(self):
        self.x += self.speed
        if self.x <= 0 or self.x >= WIDTH - self.width:
            self.speed *= -1
        self.rect.topleft = (self.x, self.y)

    def draw(self):
        pygame.draw.rect(screen, RED, self.rect)
        pygame.draw.rect(screen, GREEN, (self.x, self.y - 20, self.health, 10))

# Power Ups
class PowerUp:
    def __init__(self, x, y, type_):
        self.width = 20
        self.height = 20
        self.x = x
        self.y = y
        self.speed = 2
        self.type = type_  # "speed" or "bullets"
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def move(self):
        self.y += self.speed
        self.rect.topleft = (self.x, self.y)

    def draw(self):
        color = BLUE if self.type == "speed" else PURPLE
        pygame.draw.rect(screen, color, self.rect)

# Player attacks
def shoots_bullets_player(player, bullets):
    player_bullets = len([b for b in bullets if b.speed < 0])
    if player_bullets < player.max_bullets:
        if player.max_bullets == 2:
            bullets.append(Bullet(player.x + player.width // 2 - 2.5, player.y))
        else:
            for i in range(player.max_bullets):
                angle = -30 + (60 / (player.max_bullets - 1)) * i
                bullets.append(Bullet(player.x + player.width // 2 - 2.5, player.y, angle))

# Enemy attacks
def shoots_bullets_enemy(enemy, bullets):
    if enemy.type == "sine":
        for angle in [-15, 0, 15]:
            bullets.append(Bullet(enemy.x + enemy.width // 2 - 2.5, enemy.y + enemy.height, angle=angle, speed=5))
    else:
        bullets.append(Bullet(enemy.x + enemy.width // 2 - 2.5, enemy.y + enemy.height, speed=5))

# Boss attacks
def shoots_bullets_boss(boss, bullets):
    if boss.attack_type == 0:
        bullets.append(Bullet(boss.x + boss.width // 2 - 2.5, boss.y + boss.height, speed=5))
    elif boss.attack_type == 1:
        for angle in [-40, -20, 0, 20, 40]:
            bullets.append(Bullet(boss.x + boss.width // 2 - 2.5, boss.y + boss.height, angle=angle, speed=6))
    elif boss.attack_type == 2:
        for offset in [-20, 0, 20]:
            bullets.append(Bullet(boss.x + boss.width // 2 - 2.5 + offset, boss.y + boss.height, speed=8))
    elif boss.attack_type == 3:
        for _ in range(10):
            x = random.randint(boss.x, boss.x + boss.width)
            bullets.append(Bullet(x, boss.y + boss.height, speed=random.uniform(5, 7)))

# Reset game
def reset_game():
    player = Player()
    enemies = [Enemy(x, 50, random.choice(["normal", "sine"])) for x in range(50, WIDTH - 50, 60)]
    bullets = []
    power_ups = []
    boss = None
    round_num = 1
    level = 1
    enemy_direction = 1
    enemy_move_down = False
    return player, enemies, bullets, power_ups, boss, round_num, level, enemy_direction, enemy_move_down

# Initialization
player, enemies, bullets, power_ups, boss, round_num, level, enemy_direction, enemy_move_down = reset_game()
game_state = MENU
frame_count = 0

clock = pygame.time.Clock()
running = True

# Game loop
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if game_state == PLAYING:
                if event.key == pygame.K_SPACE:
                    shoots_bullets_player(player, bullets)
                elif event.key == pygame.K_ESCAPE:
                    game_state = PAUSED

            # Game paused
            elif game_state == PAUSED and event.key == pygame.K_ESCAPE:
                game_state = PLAYING
            elif game_state == PAUSED and event.key == pygame.K_x:
                running = False

            # Menu
            elif game_state == MENU and event.key == pygame.K_RETURN:
                game_state = PLAYING
            elif game_state == MENU and event.key == pygame.K_q:
                running = False

            # Game Over
            elif game_state == GAME_OVER and event.key == pygame.K_r:
                player, enemies, bullets, power_ups, boss, round_num, level, enemy_direction, enemy_move_down = reset_game()
                game_state = PLAYING
            elif game_state == GAME_OVER and event.key == pygame.K_q:
                running = False

    # Player movements
    if game_state == PLAYING:
        keys = pygame.key.get_pressed()
        dx = 0
        dy = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx = -player.speed
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx = player.speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy = -player.speed
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy = player.speed
        player.move(dx, dy)

        # Update timers
        player.update_timers()

        # Rounds logic
        if not enemies and not boss and not power_ups and round_num % 5 != 0:
            round_num += 1
            if round_num % 5 == 0:
                level += 1
                boss = Boss(round_num)
            else:
                enemies = [Enemy(x, 50, random.choice(["normal", "sine"])) for x in range(50, WIDTH - 50, 60)]

        # Movement and shooting of enemies
        for enemy in enemies[:]:
            enemy.move(frame_count)
            enemy.shoot_timer -= 1
            if enemy.shoot_timer <= 0:
                shoots_bullets_enemy(enemy, bullets)
                enemy.shoot_timer = random.randint(60, 180)

            # Check for collisions with the bottom
            if enemy.y + enemy.height >= HEIGHT:
                game_state = GAME_OVER
                break

            for bullet in bullets[:]:
                if bullet.speed < 0 and bullet.rect.colliderect(enemy.rect):
                    enemies.remove(enemy)
                    bullets.remove(bullet)
                    if random.random() < 0.5:
                        power_type = random.choice(["speed", "bullets"])
                        power_ups.append(PowerUp(enemy.x, enemy.y, power_type))
                    break
            if enemy.x <= 0 or enemy.x >= WIDTH - enemy.width:
                enemy_direction *= -1
                enemy_move_down = True

        if enemy_move_down:
            for enemy in enemies:
                enemy.y += 20
                enemy.rect.topleft = (enemy.x, enemy.y)
            enemy_move_down = False
        for enemy in enemies:
            enemy.speed = enemy_direction * 2

        # Boss logic
        if boss:
            boss.move()
            boss.shoot_timer -= 1
            boss.special_timer -= 1
            boss.spawn_timer -= 1

            if boss.shoot_timer <= 0:
                boss.attack_type = random.randint(0, 2)
                shoots_bullets_boss(boss, bullets)
                boss.shoot_timer = random.randint(30, 120)

            if boss.special_timer <= 0:
                boss.attack_type = 3
                shoots_bullets_boss(boss, bullets)
                boss.special_timer = 300

            # Spawn enemies every 10 seconds
            if boss.spawn_timer <= 0:
                for _ in range(4):
                    x = random.randint(50, WIDTH - 50)
                    enemies.append(Enemy(x, 50, random.choice(["normal", "sine"])))
                boss.spawn_timer = 600

        # Bullet movement
        for bullet in bullets[:]:
            bullet.move()
            if bullet.y < 0 or bullet.y > HEIGHT or bullet.x < 0 or bullet.x > WIDTH:
                bullets.remove(bullet)
            elif bullet.speed > 0 and bullet.rect.colliderect(player.rect):
                game_state = GAME_OVER
            elif boss and bullet.speed < 0 and bullet.rect.colliderect(boss.rect):
                boss.health -= 10
                bullets.remove(bullet)
                if boss.health <= 0:
                    boss = None
                    round_num += 1
                    enemies = [Enemy(x, 50, random.choice(["normal", "sine"])) for x in range(50, WIDTH - 50, 60)]  

        # Power-up movement and collection
        for power_up in power_ups[:]:
            power_up.move()
            if power_up.rect.colliderect(player.rect):
                if power_up.type == "speed":
                    if player.speed < 9:
                        player.speed += 2
                        if player.speed > 9:
                            player.speed = 9
                    player.speed_timer = 1200
                elif power_up.type == "bullets":
                    player.max_bullets += 1
                    player.bullet_timer = 1200
                power_ups.remove(power_up)
            elif power_up.y > HEIGHT:
                power_ups.remove(power_up)

    # Clear the screen
    screen.fill(BLACK)

    # Game state "MENU"
    if game_state == MENU:
        title = default_font.render("Space Invaders", True, WHITE)
        start = default_font.render("Press ENTER to Start", True, WHITE)
        exit = default_font.render("Press Q to Exit", True, WHITE)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 2 - 100))
        screen.blit(start, (WIDTH // 2 - start.get_width() // 2, HEIGHT // 2))
        screen.blit(exit, (WIDTH // 2 - exit.get_width() // 2, HEIGHT // 2 + 50))

    # Game state "PLAYING"
    elif game_state == PLAYING:
        player.draw()
        for enemy in enemies:
            enemy.draw()
        for bullet in bullets:
            bullet.draw()
        for power_up in power_ups:
            power_up.draw()
        if boss:
            boss.draw()

        # Display round and level
        text = default_font.render(f"ROUND: {round_num}  LEVEL: {level}", True, WHITE)
        screen.blit(text, (10, 10))

        # Display timers
        speed_text = default_font.render(f"Speed Timer: {player.speed_timer // 60}", True, WHITE)
        bullets_text = default_font.render(f"Bullets Timer: {player.bullet_timer // 60}", True, WHITE)
        screen.blit(speed_text, (10, 50))
        screen.blit(bullets_text, (10, 90))

    # Display game state "PAUSED"
    elif game_state == PAUSED:
        paused = default_font.render("Paused", True, WHITE)
        resume = default_font.render("Press ESC to Resume", True, WHITE)
        exit_round = default_font.render("Press X to Exit Round", True, WHITE)
        screen.blit(paused, (WIDTH // 2 - paused.get_width() // 2, HEIGHT // 2 - 50))
        screen.blit(resume, (WIDTH // 2 - resume.get_width() // 2, HEIGHT // 2))
        screen.blit(exit_round, (WIDTH // 2 - exit_round.get_width() // 2, HEIGHT // 2 + 50))

    # Display game state "GAME OVER"
    elif game_state == GAME_OVER:
        lost = default_font.render("You've Lost", True, WHITE)
        try_again = default_font.render("Press R to Try Again", True, WHITE)
        exit = default_font.render("Press Q to Exit", True, WHITE)
        screen.blit(lost, (WIDTH // 2 - lost.get_width() // 2, HEIGHT // 2 - 100))
        screen.blit(try_again, (WIDTH // 2 - try_again.get_width() // 2, HEIGHT // 2))
        screen.blit(exit, (WIDTH // 2 - exit.get_width() // 2, HEIGHT // 2 + 50))

    pygame.display.flip()
    frame_count += 1
    clock.tick(60)

pygame.quit()
sys.exit()  
