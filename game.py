import pygame
import sys
import pickle
from os import path

# General Setup
pygame.init()

SCREEN_WIDTH = 1000
SCREEN_HIGHT = 1000

clock = pygame.time.Clock()
FPS = 60
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HIGHT))
pygame.display.set_caption("game.py")

# Loading graphics
sun_img = pygame.image.load("img/sun.png")
bg_img = pygame.image.load("img/sky.png")
grass_img = pygame.image.load("img/grass.png")
restart_img = pygame.image.load("img/restart_btn.png")
start_img = pygame.image.load("img/start_btn.png")
exit_img = pygame.image.load("img/exit_btn.png")

# Define fonts
font_score = pygame.font.SysFont('Bauhaus 93', 50)

# Game variables
tile_size = 50
game_over = 0
main_menu = True
level = 1
MAX_LEVEL = 7
score = 0

# Define Colors
white = (255, 255, 255)
blue = (0, 0, 255)

# Functions go here

# Text to Screen
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x ,y))

# Reset level function
def reset_level(level):
    player.reset(100 , SCREEN_HIGHT - 130)
    blob_group.empty()
    lava_group.empty()
    exit_group.empty()

    # Load next level
    if path.exists(f'level{level}_data'):
        pickle_in = open(f'level{level}_data', 'rb')
        world_data = pickle.load(pickle_in)
    world = World(world_data)

    return world

# Buttons
class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.clicked = False
    
    def draw(self):
        action = False

        # Get Mouse Position
        pos = pygame.mouse.get_pos()
        
        # Check mouse click
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                action = True
                self.clicked = True

        # Check if mouse button is released.
        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        # Draw button
        screen.blit(self.image, self.rect)

        return action

# Player
class Player():
    def __init__(self, x, y):
        self.reset(x, y)
    
    def update(self, game_over):
        dx = 0
        dy = 0
        WALK_COOLDOWN = 5

        if game_over == False:
            # Get keypresses
            key = pygame.key.get_pressed()
            if key[pygame.K_SPACE] and self.jumped == False and self.in_air == False:
                self.vel_y = -15
                self.jumped = True
            if key[pygame.K_SPACE] == False:
                self.jumped = False
            if key[pygame.K_a]:
                dx -= 5
                self.counter += 1
                self.direction = -1
            if key[pygame.K_d]:
                dx += 5
                self.counter += 1
                self.direction = 1
            if key[pygame.K_a] == False and key[pygame.K_d] == False:
                self.counter = 0
                self.index = 0
                if self.direction == 1:
                    self.image = self.images_right[self.index]
                if self.direction == -1:
                    self.image = self.images_left[self.index]


            
            # Handle animation
            if self.counter > WALK_COOLDOWN:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images_right):
                    self.index = 0  # Make it loop once cycled
                if self.direction == 1:
                    self.image = self.images_right[self.index]
                if self.direction == -1:
                    self.image = self.images_left[self.index]

            # Gravity system
            self.vel_y += 1
            if self.vel_y > 10:
                self.vel = 10
            dy += self.vel_y

            # Check for collision
            self.in_air = True
            for tile in world.tile_list:
                # Check for collision (Left / Right)
                if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0

                # Check for collision (Up / Down)
                if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    
                    # Check if below the ground i.e jumping
                    if self.vel_y < 0:
                        dy = tile[1].bottom - self.rect.top
                        self.vel_y = 0
                        self.in_air = True

                    # Check if above the ground i.e standing
                    elif self.vel_y > 0:
                        dy = tile[1].top - self.rect.bottom
                        self.vel_y = 0
                        self.in_air = False
            
            # Check for collision (Enemies or Hazards)
            if pygame.sprite.spritecollide(self, blob_group, False):
                game_over = -1

            if pygame.sprite.spritecollide(self, lava_group, False):
                game_over = -1

            # Check for collision (Exit)
            if pygame.sprite.spritecollide(self, exit_group, False):
                game_over = 1


            # Update Player position
            self.rect.x += dx
            self.rect.y += dy

        # Player dead
        elif game_over == -1:
            self.image = self.dead_image
            draw_text('GAME OVER!', font_score, blue, (SCREEN_WIDTH // 2) - 100, SCREEN_HIGHT // 2)
            if self.rect.y > 200:
                self.rect.y -= 5

        # draw the player
        screen.blit(self.image, self.rect)
        pygame.draw.rect(screen, (255, 0, 0), self.rect, 2)
        
        return game_over

    def reset(self, x, y):
        self.images_right = []
        self.images_left = []
        self.index = 0
        self.counter = 0
        for i in range(1, 5):
            img_right = pygame.image.load(f"img/guy{i}.png")
            img_right = pygame.transform.scale(img_right, (40,80))

            img_left = pygame.transform.flip(img_right, True, False)
            
            self.images_right.append(img_right)
            self.images_left.append(img_left)

        self.dead_image = pygame.image.load("img/ghost.png")
        self.image = self.images_right[self.index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.vel_y = 0
        self.jumped = False
        self.direction = 0
        self.in_air = True

# World

class World():
    def __init__(self, data):

        self.tile_list = []

        # load world graphics
        dirt_img = pygame.image.load("img/dirt.png")

        row_count = 0
        for row in data:
            col_count = 0
            for tile in row:

                # Dirt Block
                if tile == 1:
                    img = pygame.transform.scale(dirt_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)

                # Grass Block
                if tile == 2:
                    img = pygame.transform.scale(grass_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                
                # Enemy Blob
                if tile == 3:
                    blob = Enemy(col_count * tile_size, row_count * tile_size + 15)
                    blob_group.add(blob)

                # Lava Hazard
                if tile == 6:
                    lava = Lava(col_count * tile_size, row_count * tile_size + (tile_size // 2))
                    lava_group.add(lava)

                # Monëy so big
                if tile == 7:
                    coin = Coin(col_count * tile_size + (tile_size // 2), row_count * tile_size + (tile_size // 2))
                    coin_group.add(coin)

                # Level Exit
                if tile == 8:
                    exit = Exit(col_count * tile_size, row_count * tile_size - (tile_size // 2))
                    exit_group.add(exit)
                col_count += 1
            row_count += 1


    def draw(self):
        for tile in self.tile_list:
            screen.blit(tile[0], tile[1])
            pygame.draw.rect(screen, (255, 255, 255), tile[1], 2)

# Enemies
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x , y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("img/blob.png")
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_direction = 1
        self.move_counter = 0
    
    def update(self):
        self.rect.x += self.move_direction
        self.move_counter += 1
        if abs(self.move_counter) > 50:
            self.move_direction *= -1
            self.move_counter *= -1

# Hazardous Environments
class Lava(pygame.sprite.Sprite):
    def __init__(self, x , y):
        pygame.sprite.Sprite.__init__(self)
        img  = pygame.image.load("img/lava.png")
        self.image = pygame.transform.scale(img, (tile_size, tile_size // 2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

# Monëy so big
class Coin(pygame.sprite.Sprite):
    def __init__(self, x , y):
        pygame.sprite.Sprite.__init__(self)
        img  = pygame.image.load("img/coin.png")
        self.image = pygame.transform.scale(img, (tile_size // 2, tile_size // 2))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

# Level exit class
class Exit(pygame.sprite.Sprite):
    def __init__(self, x , y):
        pygame.sprite.Sprite.__init__(self)
        img  = pygame.image.load("img/exit.png")
        self.image = pygame.transform.scale(img, (tile_size, int(tile_size * 1.5)))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

# Making Sprite groups
player = Player(100, SCREEN_HIGHT - 130)

blob_group = pygame.sprite.Group()
lava_group = pygame.sprite.Group()
coin_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()

# Load level data
if path.exists(f'level{level}_data'):
    pickle_in = open(f'level{level}_data', 'rb')
    world_data = pickle.load(pickle_in)
    world = World(world_data)

# Create Buttons
restart_button = Button(SCREEN_WIDTH // 2 - 50, SCREEN_HIGHT // 2 + 100, restart_img)
start_button = Button(SCREEN_WIDTH // 2 - 350,  SCREEN_HIGHT // 2, start_img)
exit_button = Button(SCREEN_WIDTH // 2 + 150, SCREEN_HIGHT // 2, exit_img)

# Create score coin icon
score_coin = Coin(tile_size // 2, tile_size // 2)
coin_group.add(score_coin)

# Main game loop
while True:
    
    clock.tick(FPS)

    screen.blit(bg_img, (0,0))
    screen.blit(sun_img,(100,100))

    if main_menu == True:
        if start_button.draw() == True:
            main_menu = False

        if exit_button.draw() == True:
            pygame.quit()
            sys.exit()

    else:
        world.draw()

        if game_over == 0:
            blob_group.update()

            # Coin check
            if pygame.sprite.spritecollide(player, coin_group, True):
                score += 1
            draw_text('X  ' + str(score), font_score, white, tile_size - 10, 10)

        blob_group.draw(screen)
        lava_group.draw(screen)
        coin_group.draw(screen)
        exit_group.draw(screen)

        game_over = player.update(game_over)

        # Game Over
        if game_over == -1:
            if restart_button.draw():
                world_data = []
                world = reset_level(level)
                game_over = 0
                score = 0

        # When the Player wins    
        if game_over == 1:
            # Reset game and go to next level
            level += 1
            if level <= MAX_LEVEL:
                world_data = []
                world = reset_level(level)
                game_over = 0
            else:
                draw_text("YOU WIN!", font_score, blue, (SCREEN_WIDTH // 2) -140 , SCREEN_HIGHT // 2)
                if restart_button.draw():
                    level = 1
                    # Reset level
                    world_data = []
                    world = reset_level(level)
                    game_over = 0

    # Exit manager
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    pygame.display.update()