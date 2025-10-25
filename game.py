import pygame
import random
import math
import sys

# Initialize pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pixel Shooter")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 50, 50)
GREEN = (50, 255, 50)
BLUE = (50, 100, 255)
YELLOW = (255, 255, 50)
PURPLE = (180, 50, 230)
CYAN = (0, 200, 200)
ORANGE = (255, 150, 0)

# Clock for controlling frame rate
clock = pygame.time.Clock()
FPS = 60

# Player class
class Player:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT - 100
        self.width = 40
        self.height = 40
        self.speed = 5
        self.color = BLUE
        self.health = 100
        self.max_health = 100
        self.weapon = "Pistol"
        self.weapons = {
            "Pistol": {"damage": 10, "fire_rate": 0.5, "color": WHITE, "bullet_speed": 10},
            "Shotgun": {"damage": 5, "fire_rate": 1.0, "color": YELLOW, "bullet_speed": 12},
            "Laser": {"damage": 20, "fire_rate": 0.2, "color": RED, "bullet_speed": 15}
        }
        self.last_shot = 0
        self.score = 0
        self.invincible = 0
        self.power_up_timer = 0
        self.power_up_type = None

    def draw(self, screen):
        # Draw player ship
        pygame.draw.polygon(screen, self.color, [
            (self.x, self.y - self.height//2),
            (self.x - self.width//2, self.y + self.height//2),
            (self.x + self.width//2, self.y + self.height//2)
        ])
        
        # Draw engine glow
        glow_size = random.randint(5, 10)
        pygame.draw.polygon(screen, YELLOW, [
            (self.x - 10, self.y + self.height//2),
            (self.x, self.y + self.height//2 + glow_size),
            (self.x + 10, self.y + self.height//2)
        ])
        
        # Draw health bar
        bar_width = 50
        bar_height = 6
        pygame.draw.rect(screen, RED, (self.x - bar_width//2, self.y - 40, bar_width, bar_height))
        pygame.draw.rect(screen, GREEN, (self.x - bar_width//2, self.y - 40, bar_width * (self.health / self.max_health), bar_height))
        
        # Draw weapon indicator
        font = pygame.font.SysFont(None, 20)
        weapon_text = font.render(f"Weapon: {self.weapon}", True, self.weapons[self.weapon]["color"])
        screen.blit(weapon_text, (self.x - weapon_text.get_width()//2, self.y - 60))
        
        # Draw invincibility effect
        if self.invincible > 0:
            pygame.draw.circle(screen, CYAN, (self.x, self.y), 30, 2)

    def move(self, keys):
        if keys[pygame.K_LEFT] and self.x - self.width//2 > 0:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] and self.x + self.width//2 < WIDTH:
            self.x += self.speed
        if keys[pygame.K_UP] and self.y - self.height//2 > 0:
            self.y -= self.speed
        if keys[pygame.K_DOWN] and self.y + self.height//2 < HEIGHT:
            self.y += self.speed

    def shoot(self, bullets):
        current_time = pygame.time.get_ticks()
        weapon = self.weapons[self.weapon]
        
        if current_time - self.last_shot > 1000 / weapon["fire_rate"]:
            self.last_shot = current_time
            
            if self.weapon == "Pistol":
                bullets.append(Bullet(self.x, self.y - 20, 0, -weapon["bullet_speed"], weapon["damage"], weapon["color"]))
            elif self.weapon == "Shotgun":
                for angle in [-10, 0, 10]:
                    rad_angle = math.radians(angle)
                    bullets.append(Bullet(
                        self.x, self.y - 20, 
                        math.sin(rad_angle) * 3, 
                        -math.cos(rad_angle) * weapon["bullet_speed"], 
                        weapon["damage"], weapon["color"]
                    ))
            elif self.weapon == "Laser":
                bullets.append(LaserBeam(self.x, self.y - 20, weapon["damage"], weapon["color"]))
                
            return True
        return False

    def take_damage(self, amount):
        if self.invincible <= 0:
            self.health -= amount
            self.invincible = 30  # Invincibility frames
            return True
        return False

    def update(self):
        if self.invincible > 0:
            self.invincible -= 1
            
        if self.power_up_timer > 0:
            self.power_up_timer -= 1
            if self.power_up_timer == 0:
                self.weapon = "Pistol"  # Revert to default weapon

    def apply_power_up(self, power_type):
        if power_type == "health":
            self.health = min(self.health + 30, self.max_health)
        elif power_type == "shotgun":
            self.weapon = "Shotgun"
            self.power_up_type = "shotgun"
            self.power_up_timer = 300  # 5 seconds at 60 FPS
        elif power_type == "laser":
            self.weapon = "Laser"
            self.power_up_type = "laser"
            self.power_up_timer = 300

# Bullet class
class Bullet:
    def __init__(self, x, y, dx, dy, damage, color):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.damage = damage
        self.color = color
        self.radius = 4
        self.trail = []

    def update(self):
        self.trail.append((self.x, self.y))
        if len(self.trail) > 5:
            self.trail.pop(0)
            
        self.x += self.dx
        self.y += self.dy

    def draw(self, screen):
        # Draw trail
        for i, pos in enumerate(self.trail):
            alpha = 100 - i * 20
            if alpha > 0:
                trail_surf = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA)
                pygame.draw.circle(trail_surf, (*self.color, alpha), (self.radius, self.radius), self.radius)
                screen.blit(trail_surf, (pos[0] - self.radius, pos[1] - self.radius))
        
        # Draw bullet
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.radius - 1)

    def is_off_screen(self):
        return (self.x < 0 or self.x > WIDTH or 
                self.y < 0 or self.y > HEIGHT)

# Laser beam class (special weapon)
class LaserBeam:
    def __init__(self, x, y, damage, color):
        self.x = x
        self.y = y
        self.damage = damage
        self.color = color
        self.width = 6
        self.height = HEIGHT - y
        self.active = True
        self.timer = 10  # Frames the laser stays active

    def update(self):
        self.timer -= 1
        if self.timer <= 0:
            self.active = False

    def draw(self, screen):
        if self.active:
            # Draw main beam
            pygame.draw.rect(screen, self.color, (self.x - self.width//2, self.y, self.width, self.height))
            
            # Draw glow effect
            for i in range(3):
                glow_width = self.width + i * 4
                alpha = 150 - i * 50
                glow_surf = pygame.Surface((glow_width, self.height), pygame.SRCALPHA)
                pygame.draw.rect(glow_surf, (*self.color, alpha), (0, 0, glow_width, self.height))
                screen.blit(glow_surf, (self.x - glow_width//2, self.y))

    def is_off_screen(self):
        return not self.active

# Enemy class
class Enemy:
    def __init__(self, x, y, enemy_type="basic"):
        self.x = x
        self.y = y
        self.type = enemy_type
        
        if enemy_type == "basic":
            self.width = 30
            self.height = 30
            self.speed = 2
            self.health = 20
            self.color = RED
            self.score_value = 10
        elif enemy_type == "fast":
            self.width = 20
            self.height = 20
            self.speed = 4
            self.health = 10
            self.color = ORANGE
            self.score_value = 15
        elif enemy_type == "tank":
            self.width = 50
            self.height = 50
            self.speed = 1
            self.health = 60
            self.color = PURPLE
            self.score_value = 30
            
        self.max_health = self.health
        self.shoot_timer = 0
        self.bullets = []

    def update(self):
        self.y += self.speed
        
        # Enemy shooting logic
        self.shoot_timer += 1
        if self.shoot_timer > 60 and random.random() < 0.02:  # Shoot every ~2 seconds with some randomness
            self.shoot_timer = 0
            self.bullets.append(Bullet(self.x, self.y + self.height//2, 0, 5, 5, RED))

    def draw(self, screen):
        # Draw enemy based on type
        if self.type == "basic":
            pygame.draw.rect(screen, self.color, (self.x - self.width//2, self.y - self.height//2, self.width, self.height))
            # Draw details
            pygame.draw.rect(screen, BLACK, (self.x - self.width//4, self.y - self.height//4, self.width//2, self.height//2))
        elif self.type == "fast":
            pygame.draw.polygon(screen, self.color, [
                (self.x, self.y - self.height//2),
                (self.x - self.width//2, self.y + self.height//2),
                (self.x + self.width//2, self.y + self.height//2)
            ])
        elif self.type == "tank":
            pygame.draw.circle(screen, self.color, (self.x, self.y), self.width//2)
            pygame.draw.circle(screen, BLACK, (self.x, self.y), self.width//4)
            
        # Draw health bar
        bar_width = self.width
        bar_height = 4
        pygame.draw.rect(screen, RED, (self.x - bar_width//2, self.y - self.height//2 - 10, bar_width, bar_height))
        pygame.draw.rect(screen, GREEN, (self.x - bar_width//2, self.y - self.height//2 - 10, 
                                         bar_width * (self.health / self.max_health), bar_height))

    def is_off_screen(self):
        return self.y > HEIGHT + self.height

    def take_damage(self, amount):
        self.health -= amount
        return self.health <= 0

# Power-up class
class PowerUp:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 20
        self.height = 20
        self.speed = 2
        self.type = random.choice(["health", "shotgun", "laser"])
        
        if self.type == "health":
            self.color = GREEN
        elif self.type == "shotgun":
            self.color = YELLOW
        elif self.type == "laser":
            self.color = RED

    def update(self):
        self.y += self.speed

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x - self.width//2, self.y - self.height//2, self.width, self.height))
        
        # Draw symbol based on type
        if self.type == "health":
            pygame.draw.rect(screen, WHITE, (self.x - 5, self.y - 8, 10, 16), 2)
            pygame.draw.rect(screen, WHITE, (self.x - 8, self.y - 5, 16, 10), 2)
        elif self.type == "shotgun":
            pygame.draw.rect(screen, WHITE, (self.x - 6, self.y, 12, 4))
            pygame.draw.circle(screen, WHITE, (self.x, self.y - 4), 3)
        elif self.type == "laser":
            pygame.draw.line(screen, WHITE, (self.x - 6, self.y - 6), (self.x + 6, self.y + 6), 2)
            pygame.draw.line(screen, WHITE, (self.x - 6, self.y + 6), (self.x + 6, self.y - 6), 2)

    def is_off_screen(self):
        return self.y > HEIGHT + self.height

# Particle effect for explosions
class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.size = random.randint(2, 6)
        self.speed_x = random.uniform(-3, 3)
        self.speed_y = random.uniform(-3, 3)
        self.life = random.randint(20, 40)

    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        self.life -= 1
        self.size = max(0, self.size - 0.1)

    def draw(self, screen):
        alpha = min(255, self.life * 6)
        particle_surf = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.circle(particle_surf, (*self.color, alpha), (self.size, self.size), self.size)
        screen.blit(particle_surf, (self.x - self.size, self.y - self.size))

    def is_dead(self):
        return self.life <= 0

# Game class to manage everything
class Game:
    def __init__(self):
        self.player = Player()
        self.bullets = []
        self.enemies = []
        self.power_ups = []
        self.particles = []
        self.enemy_spawn_timer = 0
        self.score = 0
        self.game_over = False
        self.wave = 1
        self.enemies_killed = 0
        self.background_stars = [(random.randint(0, WIDTH), random.randint(0, HEIGHT), random.randint(1, 3)) 
                                for _ in range(100)]

    def spawn_enemy(self):
        self.enemy_spawn_timer += 1
        spawn_rate = max(20, 60 - self.wave * 5)  # Spawn rate increases with waves
        
        if self.enemy_spawn_timer > spawn_rate:
            self.enemy_spawn_timer = 0
            
            # Determine enemy type based on wave
            rand = random.random()
            if self.wave < 3:
                enemy_type = "basic"
            elif self.wave < 5:
                enemy_type = "basic" if rand < 0.7 else "fast"
            else:
                if rand < 0.5:
                    enemy_type = "basic"
                elif rand < 0.8:
                    enemy_type = "fast"
                else:
                    enemy_type = "tank"
                    
            x = random.randint(50, WIDTH - 50)
            self.enemies.append(Enemy(x, -50, enemy_type))

    def spawn_power_up(self, x, y):
        if random.random() < 0.2:  # 20% chance to spawn power-up
            self.power_ups.append(PowerUp(x, y))

    def check_collisions(self):
        # Player bullets vs enemies
        for bullet in self.bullets[:]:
            for enemy in self.enemies[:]:
                if (abs(bullet.x - enemy.x) < (bullet.radius + enemy.width//2) and
                    abs(bullet.y - enemy.y) < (bullet.radius + enemy.height//2)):
                    
                    if enemy.take_damage(bullet.damage):
                        # Enemy destroyed
                        self.score += enemy.score_value
                        self.enemies_killed += 1
                        self.spawn_power_up(enemy.x, enemy.y)
                        
                        # Create explosion particles
                        for _ in range(20):
                            self.particles.append(Particle(enemy.x, enemy.y, enemy.color))
                        
                        self.enemies.remove(enemy)
                    
                    if bullet in self.bullets:
                        self.bullets.remove(bullet)
                    break

        # Laser vs enemies
        for bullet in self.bullets[:]:
            if isinstance(bullet, LaserBeam) and bullet.active:
                for enemy in self.enemies[:]:
                    if (abs(bullet.x - enemy.x) < (bullet.width//2 + enemy.width//2) and
                        enemy.y > bullet.y):
                        
                        if enemy.take_damage(bullet.damage):
                            # Enemy destroyed
                            self.score += enemy.score_value
                            self.enemies_killed += 1
                            self.spawn_power_up(enemy.x, enemy.y)
                            
                            # Create explosion particles
                            for _ in range(20):
                                self.particles.append(Particle(enemy.x, enemy.y, enemy.color))
                            
                            self.enemies.remove(enemy)

        # Enemy bullets vs player
        for enemy in self.enemies:
            for bullet in enemy.bullets[:]:
                if (abs(bullet.x - self.player.x) < (bullet.radius + self.player.width//2) and
                    abs(bullet.y - self.player.y) < (bullet.radius + self.player.height//2)):
                    
                    if self.player.take_damage(bullet.damage):
                        # Create hit particles
                        for _ in range(10):
                            self.particles.append(Particle(self.player.x, self.player.y, RED))
                    
                    if bullet in enemy.bullets:
                        enemy.bullets.remove(bullet)
                    break

        # Enemies vs player (collision damage)
        for enemy in self.enemies[:]:
            if (abs(enemy.x - self.player.x) < (enemy.width//2 + self.player.width//2) and
                abs(enemy.y - self.player.y) < (enemy.height//2 + self.player.height//2)):
                
                if self.player.take_damage(10):
                    # Create hit particles
                    for _ in range(15):
                        self.particles.append(Particle(self.player.x, self.player.y, RED))
                
                # Create explosion and remove enemy
                for _ in range(20):
                    self.particles.append(Particle(enemy.x, enemy.y, enemy.color))
                
                self.enemies.remove(enemy)
                self.score += enemy.score_value
                self.enemies_killed += 1

        # Power-ups vs player
        for power_up in self.power_ups[:]:
            if (abs(power_up.x - self.player.x) < (power_up.width//2 + self.player.width//2) and
                abs(power_up.y - self.player.y) < (power_up.height//2 + self.player.height//2)):
                
                self.player.apply_power_up(power_up.type)
                
                # Create collection particles
                for _ in range(15):
                    self.particles.append(Particle(power_up.x, power_up.y, power_up.color))
                
                self.power_ups.remove(power_up)

    def update(self):
        if self.game_over:
            return
            
        # Update player
        self.player.update()
        
        # Update bullets
        for bullet in self.bullets[:]:
            bullet.update()
            if bullet.is_off_screen():
                self.bullets.remove(bullet)
                
        # Update enemies and their bullets
        for enemy in self.enemies[:]:
            enemy.update()
            
            for bullet in enemy.bullets[:]:
                bullet.update()
                if bullet.is_off_screen():
                    enemy.bullets.remove(bullet)
                    
            if enemy.is_off_screen():
                self.enemies.remove(enemy)
                
        # Update power-ups
        for power_up in self.power_ups[:]:
            power_up.update()
            if power_up.is_off_screen():
                self.power_ups.remove(power_up)
                
        # Update particles
        for particle in self.particles[:]:
            particle.update()
            if particle.is_dead():
                self.particles.remove(particle)
                
        # Spawn enemies
        self.spawn_enemy()
        
        # Check collisions
        self.check_collisions()
        
        # Check for game over
        if self.player.health <= 0:
            self.game_over = True
            
        # Update wave based on enemies killed
        if self.enemies_killed >= self.wave * 10:
            self.wave += 1
            self.enemies_killed = 0

    def draw(self, screen):
        # Draw background
        screen.fill(BLACK)
        
        # Draw stars
        for x, y, size in self.background_stars:
            pygame.draw.circle(screen, WHITE, (x, y), size)
        
        # Draw player
        self.player.draw(screen)
        
        # Draw bullets
        for bullet in self.bullets:
            bullet.draw(screen)
            
        # Draw enemies and their bullets
        for enemy in self.enemies:
            enemy.draw(screen)
            for bullet in enemy.bullets:
                bullet.draw(screen)
                
        # Draw power-ups
        for power_up in self.power_ups:
            power_up.draw(screen)
            
        # Draw particles
        for particle in self.particles:
            particle.draw(screen)
            
        # Draw HUD
        font = pygame.font.SysFont(None, 36)
        score_text = font.render(f"Score: {self.score}", True, WHITE)
        screen.blit(score_text, (10, 10))
        
        wave_text = font.render(f"Wave: {self.wave}", True, WHITE)
        screen.blit(wave_text, (WIDTH - wave_text.get_width() - 10, 10))
        
        # Draw game over screen
        if self.game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            
            game_over_font = pygame.font.SysFont(None, 72)
            game_over_text = game_over_font.render("GAME OVER", True, RED)
            screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2 - 50))
            
            score_font = pygame.font.SysFont(None, 48)
            final_score_text = score_font.render(f"Final Score: {self.score}", True, WHITE)
            screen.blit(final_score_text, (WIDTH//2 - final_score_text.get_width()//2, HEIGHT//2 + 20))
            
            restart_font = pygame.font.SysFont(None, 36)
            restart_text = restart_font.render("Press R to Restart", True, GREEN)
            screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 80))

# Main game loop
def main():
    game = Game()
    running = True
    
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not game.game_over:
                    game.player.shoot(game.bullets)
                elif event.key == pygame.K_r and game.game_over:
                    game = Game()  # Restart game
                    
        # Get pressed keys for continuous movement
        keys = pygame.key.get_pressed()
        if not game.game_over:
            game.player.move(keys)
            
            # Auto-fire when holding space
            if keys[pygame.K_SPACE]:
                game.player.shoot(game.bullets)
        
        # Update game state
        game.update()
        
        # Draw everything
        game.draw(screen)
        
        # Update display
        pygame.display.flip()
        
        # Control frame rate
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
