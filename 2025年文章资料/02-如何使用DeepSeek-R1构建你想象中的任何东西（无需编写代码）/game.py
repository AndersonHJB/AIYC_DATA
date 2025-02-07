import pygame
import random
import math

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Space Invaders")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Player settings
PLAYER_SPEED = 5
BULLET_SPEED = 7
MAX_BULLETS = 3
ALIEN_SPEED = 1
ALIEN_DROP = 10

# Initialize mixer for sound
pygame.mixer.init()
shoot_sound = pygame.mixer.Sound("./data/shoot.mp3")  # Add a shoot sound file
explosion_sound = pygame.mixer.Sound("./data/explosion.mp3")  # Add an explosion sound file

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((50, 30))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = SCREEN_HEIGHT - 10
        self.speed = PLAYER_SPEED
        self.bullets = pygame.sprite.Group()
        self.shoot_delay = 300
        self.last_shot = pygame.time.get_ticks()

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += self.speed
        
        self.rect.clamp_ip(screen.get_rect())

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            bullet = Bullet(self.rect.centerx, self.rect.top)
            self.bullets.add(bullet)
            shoot_sound.play()

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((5, 10))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speed = -BULLET_SPEED

    def update(self):
        self.rect.y += self.speed
        if self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT:
            self.kill()

class Alien(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((40, 30))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = ALIEN_SPEED
        self.drop = ALIEN_DROP
        self.direction = 1
        self.shoot_prob = 0.001  # Probability to shoot each frame

    def update(self):
        self.rect.x += self.speed * self.direction
        if random.random() < self.shoot_prob:
            self.shoot()

    def shoot(self):
        bullet = AlienBullet(self.rect.centerx, self.rect.bottom)
        alien_bullets.add(bullet)

class AlienBullet(Bullet):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.image.fill(RED)
        self.speed = BULLET_SPEED

class Barrier(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((80, 30))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.health = 3

    def hit(self):
        self.health -= 1
        if self.health <= 0:
            self.kill()

# Sprite groups
all_sprites = pygame.sprite.Group()
aliens = pygame.sprite.Group()
player_bullets = pygame.sprite.Group()
alien_bullets = pygame.sprite.Group()
barriers = pygame.sprite.Group()

# Create player
player = Player()
all_sprites.add(player)

# Create aliens
def create_aliens():
    for row in range(4):
        for col in range(10):
            alien = Alien(100 + col * 60, 50 + row * 40)
            aliens.add(alien)
            all_sprites.add(alien)

# Create barriers
def create_barriers():
    for x in range(4):
        barrier = Barrier(100 + x * 200, SCREEN_HEIGHT - 150)
        barriers.add(barrier)
        all_sprites.add(barrier)

create_aliens()
create_barriers()

# Game variables
score = 0
lives = 3
game_over = False
clock = pygame.time.Clock()
running = True

# Font for display
font = pygame.font.Font(None, 36)

def show_game_over():
    text = font.render("GAME OVER! Press R to restart", True, WHITE)
    text_rect = text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2))
    screen.blit(text, text_rect)

def reset_game():
    global score, lives, game_over
    aliens.empty()
    alien_bullets.empty()
    player_bullets.empty()
    barriers.empty()
    all_sprites.empty()
    
    player.rect.centerx = SCREEN_WIDTH // 2
    all_sprites.add(player)
    create_aliens()
    create_barriers()
    
    score = 0
    lives = 3
    game_over = False

# Main game loop
while running:
    screen.fill(BLACK)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not game_over:
                player.shoot()
            if event.key == pygame.K_r and game_over:
                reset_game()

    if not game_over:
        # Update
        all_sprites.update()
        
        # Check collisions
        hits = pygame.sprite.groupcollide(aliens, player_bullets, True, True)
        for hit in hits:
            score += 10
            explosion_sound.play()
        
        # Check if aliens hit barriers
        pygame.sprite.groupcollide(aliens, barriers, True, True)
        
        # Check alien bullets hit barriers
        barrier_hits = pygame.sprite.groupcollide(barriers, alien_bullets, False, True)
        for barrier in barrier_hits:
            barrier.hit()
        
        # Check player hit by alien bullets
        if pygame.sprite.spritecollide(player, alien_bullets, True):
            lives -= 1
            if lives <= 0:
                game_over = True
        
        # Check if aliens reach bottom
        for alien in aliens:
            if alien.rect.bottom >= SCREEN_HEIGHT - 50:
                lives = 0
                game_over = True
        
        # Alien movement
        move_down = False
        for alien in aliens:
            if alien.rect.right >= SCREEN_WIDTH or alien.rect.left <= 0:
                for a in aliens:
                    a.direction *= -1
                    a.rect.y += a.drop
                break
        
        # Spawn new wave if all aliens are dead
        if len(aliens) == 0:
            create_aliens()
            ALIEN_SPEED += 0.5

    # Draw
    all_sprites.draw(screen)
    player.bullets.draw(screen)
    
    # Display score and lives
    score_text = font.render(f"Score: {score}", True, WHITE)
    lives_text = font.render(f"Lives: {lives}", True, WHITE)
    screen.blit(score_text, (10, 10))
    screen.blit(lives_text, (SCREEN_WIDTH - 120, 10))
    
    if game_over:
        show_game_over()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()