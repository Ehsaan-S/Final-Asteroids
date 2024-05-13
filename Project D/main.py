import pygame
import math
import random

screen_width = 600
screen_height = 600

class SpaceRocks:
    def __init__(self):
        # Initialize pygame and screen dimensions
        self.init_pygame()
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        
        # Initialize score and lives
        self.score = 0  
        self.lives = 3  
        self.powerup_ready=False
        self.powerup_score=0
        self.powerup_timer=0
        self.powerup_duration=10000

        # Player attributes
        self.player_size = 20
        self.player_x = screen_width // 2
        self.player_y = screen_height // 2
        self.player_img_original = pygame.image.load("Project D/spaceship.gif")
        self.player_img_original = pygame.transform.scale(self.player_img_original, (50, 50))
        self.player_img = self.player_img_original
        self.player_angle = 0

        # Bullets attributes
        self.bullets = []
        self.bullet_size = 5
        self.bullet_speed = 0.5

        # Background image
        self.background_img = pygame.image.load("Project D/background.jpg")
        self.background_img = pygame.transform.scale(self.background_img, (screen_width, screen_height))

        # Asteroids attributes
        self.asteroids = []
        self.initial_asteroids_size = 15  
        self.asteroids_frozen=False
        self.freeze_time=0

    def main_loop(self):
        # Main game loop
        running = True
        while running:
            # Handle input events
            self.handle_input()
            # Process game logic
            self.process_game_logic()
            self.draw()
            if self.lives <= 0:
                self.game_over()
                print("Game Over! Your final score was:", self.score)
                running = False

    def init_pygame(self):
        # Initialize pygame
        pygame.init()
        pygame.display.set_caption("Asteroids")

    def handle_input(self):
        # Handle user input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            # Shoot bullets on mouse click
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.shoot_bullet()     
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and self.powerup_ready:
                self.activate_powerup()

    def shoot_bullet(self):
        rad_angle = math.radians(self.player_angle + 90)
        bullet_dx = math.cos(rad_angle) * self.bullet_speed
        bullet_dy = -math.sin(rad_angle) * self.bullet_speed
        self.bullets.append((self.player_x + 25, self.player_y + 25, bullet_dx, bullet_dy))
    
    def activate_powerup(self):
        if self.powerup_ready:
            self.asteroids_frozen=True
            self.freeze_time=pygame.time.get_ticks()+self.powerup_duration
            self.powerup_timer=self.freeze_time
            self.powerup_ready=False
            self.powerup_score=self.score

    def process_game_logic(self):
        # Process game logic
        self.handle_player_movement()
        self.generate_asteroids()
        self.move_asteroids()
        self.check_collisions()
        self.update_bullets()
        self.update_powerup_status()
        self.manage_powerup_duration()

    def handle_player_movement(self):
        # Handle player movement and boundaries
        mouse_x, mouse_y = pygame.mouse.get_pos()
        rel_x, rel_y = mouse_x - (self.player_x + 25), mouse_y - (self.player_y + 25)
        # Calculate player angle based on mouse
        self.player_angle = (180 / math.pi) * -math.atan2(rel_y, rel_x) - 90
        self.player_img = pygame.transform.rotate(self.player_img_original, self.player_angle)
        keys = pygame.key.get_pressed()
        # move on wasd
        if keys[pygame.K_a]:
            self.player_x -= 0.15
        if keys[pygame.K_d]:
            self.player_x += 0.15
        if keys[pygame.K_s]:
            self.player_y += 0.15
        if keys[pygame.K_w]:
            self.player_y -= 0.15
        # boundary
        if self.player_x < 0:
            self.player_x = 0
        if self.player_x > screen_width - 50:
            self.player_x = screen_width - 50
        if self.player_y < 0:
            self.player_y = 0
        if self.player_y > screen_height - 50:
            self.player_y = screen_height - 50

    def generate_asteroids(self):
        # Asteroids generation
        if not self.asteroids_frozen and len(self.asteroids) < 10 and random.randint(0, 100) < 10:
            asteroid_x = random.randint(0, screen_width)
            asteroid_y = random.randint(0, screen_height)
            speed_x = random.choice([-0.1, 0.1])
            speed_y = random.choice([-0.1, 0.1])
            self.asteroids.append((asteroid_x, asteroid_y, speed_x, speed_y, self.initial_asteroids_size))

    def move_asteroids(self):
        if not self.asteroids_frozen:
            new_asteroids = []
            for x, y, speed_x, speed_y, size in self.asteroids:
                x += speed_x
                y += speed_y
                # Handle asteroid bouncing off screen edges
                if x < 0 or x > screen_width:
                    speed_x = -speed_x
                if y < 0 or y > screen_height:
                    speed_y = -speed_y
                new_asteroids.append((x, y, speed_x, speed_y, size))
            self.asteroids = new_asteroids

    
    def check_collisions(self):
   
        for asteroid in self.asteroids:  
            asteroid_x, asteroid_y, _, _, size = asteroid  
            player_center_x = self.player_x + 25  
            player_center_y = self.player_y + 25  
        
        
            if math.hypot(asteroid_x - player_center_x, asteroid_y - player_center_y) < size + 25:
                self.asteroids.remove(asteroid)
                self.lives -= 1


        # Update bullets asteroid collision
        updated_bullets = []
        for bullet_x, bullet_y, bullet_dx, bullet_dy in self.bullets:
            bullet_hit = False
            for asteroid_x, asteroid_y, asteroid_speed_x, asteroid_speed_y, asteroid_size in self.asteroids:
                if math.hypot(asteroid_x - bullet_x, asteroid_y - bullet_y) < asteroid_size + self.bullet_size:
                    bullet_hit = True
                    self.asteroids.remove((asteroid_x, asteroid_y, asteroid_speed_x, asteroid_speed_y, asteroid_size))
                    # Split large asteroids in 2
                    if asteroid_size > 7.5:
                        for i in range(2):
                            new_asteroid_size = 7.5
                            new_asteroid_x = asteroid_x + random.randint(-5, 5)
                            new_asteroid_y = asteroid_y + random.randint(-5, 5)
                            new_asteroid_speed_x = random.choice([-0.1, 0.1]) 
                            new_asteroid_speed_y = random.choice([-0.1, 0.1]) 
                            self.asteroids.append((new_asteroid_x, new_asteroid_y, new_asteroid_speed_x, new_asteroid_speed_y, new_asteroid_size))
                        self.score += 5  # +5 for big asteroids
                    else:
                        self.score += 10  # +10 for little asteroids
                    break
            if not bullet_hit:
                updated_bullets.append((bullet_x + bullet_dx, bullet_y + bullet_dy, bullet_dx, bullet_dy))
        self.bullets = updated_bullets

    def update_bullets(self):
        # Update bullets position
        updated_bullets = []
        for bullet_x, bullet_y, bullet_dx, bullet_dy in self.bullets:
            updated_bullets.append((bullet_x + bullet_dx, bullet_y + bullet_dy, bullet_dx, bullet_dy))
        self.bullets = updated_bullets
    
    def update_powerup_status(self):
        if self.score>=self.powerup_score+500:
            self.powerup_ready=True
            
    
    def manage_powerup_duration(self):
        if self.asteroids_frozen and pygame.time.get_ticks()>self.freeze_time:
            self.asteroids_frozen=False


    def draw(self):
        # Draw game elements
        self.screen.blit(self.background_img, (0, 0))
        rotated_rect = self.player_img.get_rect(center=(self.player_x + 25, self.player_y + 25))
        self.screen.blit(self.player_img, rotated_rect.topleft)

        for bullet in self.bullets:
            # Draw bullets
            pygame.draw.circle(self.screen, (255, 255, 0), (int(bullet[0]), int(bullet[1])), self.bullet_size)

        for asteroid in self.asteroids:
            # Draw asteroids
            x, y, _, _, size = asteroid
            pygame.draw.circle(self.screen, (255, 0, 0), (int(x), int(y)), int(size))

        # Display score and livaaaaaes
        font = pygame.font.SysFont("arial", 36)
        self.screen.blit(font.render(f"Score: {self.score}", True, (255, 255, 255)), (10, 10))
        self.screen.blit(font.render(f"Lives: {self.lives}", True, (255, 255, 255)), (10, 50))
        self.screen.blit(font.render(f"Power-Up: {'Ready' if self.powerup_ready else 'Charging'}", True, (255, 255, 255)), (10, 90))

        if self.asteroids_frozen:
            current_time=pygame.time.get_ticks()
            remaining_time=max(0,(self.powerup_timer-current_time)//1000)
            self.screen.blit(font.render(f"Powerup TIme: {remaining_time}",True,(255,255,255,)),(10,130))
        pygame.display.flip()

    def game_over(self):
        self.screen.fill((0, 0, 0))
        game_over_font = pygame.font.SysFont("arial", 64)
        score_font = pygame.font.SysFont("arial", 32)
        game_over_text = game_over_font.render("Game Over", True, (255, 255, 255))
        game_over_rect = game_over_text.get_rect(center=(screen_width / 2, screen_height / 2 - 40))
        score_text = score_font.render(f"Final Score: {self.score}", True, (255, 255, 255))
        score_rect = score_text.get_rect(center=(screen_width / 2, screen_height / 2 + 20))
        self.screen.blit(game_over_text, game_over_rect)
        self.screen.blit(score_text, score_rect)
        pygame.display.flip()
        pygame.time.wait(3000)


game = SpaceRocks()
game.main_loop()
