import pygame
import sys

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

# World Grid
tile_size = 50

# Player
class Player():
    def __init__(self, x, y):
        self.images_right = []
        self.images_left = []
        self.index = 0
        self.counter = 0
        for i in range(1, 5):
            img_right = pygame.image.load(f'img/guy{i}.png')
            img_right = pygame.transform.scale(img_right, (40,80))

            img_left = pygame.transform.flip(img_right, True, False)
            
            self.images_right.append(img_right)
            self.images_left.append(img_left)

        self.image = self.images_right[self.index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.vel_y = 0
        self.jumped = False
        self.direction = 0
    
    def update(self):
        dx = 0
        dy = 0
        WALK_COOLDOWN = 5

        # get keypresses
        key = pygame.key.get_pressed()
        if key[pygame.K_a] == True:     # Left
            dx -= 5
            self.counter += 1
            self.direction = -1
        if key[pygame.K_d] == True:     # Right
            dx += 5
            self.counter += 1
            self.direction = 1
        if key[pygame.K_SPACE] == True and self.jumped == False:
            self.vel_y = -15
            self.jumped = True
        if key[pygame.K_SPACE] == True:
            self.jumped == False
        if key[pygame.K_a] == False and key[pygame.K_d] == False:   # Idle
            self.counter = 0
            self.index = 0
            if self.direction == 1:
                self.image = self.images_right[self.index]
            if self.direction == -1:
                self.image = self.images_left[self.index]


        
        # handle animation
        if self.counter > WALK_COOLDOWN:
            self.counter = 0
            self.index += 1
            if self.index >= len(self.images_right):
                self.index = 0  # Make it loop once cycled
            if self.direction == 1:
                self.image = self.images_right[self.index]
            if self.direction == -1:
                self.image = self.images_left[self.index]

        # add gravity lol
        self.vel_y += 1
        if self.vel_y > 10:
            self.vel = 10
        dy += self.vel_y

        #TODO Check for collision

        # Update Player position
        self.rect.x += dx
        self.rect.y += dy

        if self.rect.bottom > SCREEN_HIGHT:
            self.rect.bottom = SCREEN_HIGHT
            dy = 0
            self.jumped = False

        # draw the player
        screen.blit(self.image, self.rect)

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
                if tile == 1:
                    img = pygame.transform.scale(dirt_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 2:
                    img = pygame.transform.scale(grass_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                col_count += 1
            row_count += 1


    def draw(self):
        for tile in self.tile_list:
            screen.blit(tile[0], tile[1])

world_data = [
[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], 
[1, 0, 0, 0, 0, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 1], 
[1, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 7, 0, 0, 0, 0, 0, 2, 2, 1], 
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 0, 7, 0, 5, 0, 0, 0, 1], 
[1, 0, 0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 2, 2, 0, 0, 0, 0, 0, 1], 
[1, 7, 0, 0, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], 
[1, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], 
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 0, 0, 7, 0, 0, 0, 0, 1], 
[1, 0, 2, 0, 0, 7, 0, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], 
[1, 0, 0, 2, 0, 0, 4, 0, 0, 0, 0, 3, 0, 0, 3, 0, 0, 0, 0, 1], 
[1, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 2, 2, 0, 0, 0, 1], 
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], 
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 0, 7, 0, 0, 0, 0, 2, 0, 1], 
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], 
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 2, 0, 2, 2, 2, 2, 2, 1], 
[1, 0, 0, 0, 0, 0, 2, 2, 2, 6, 6, 6, 6, 6, 1, 1, 1, 1, 1, 1], 
[1, 0, 0, 0, 0, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 
[1, 0, 0, 0, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 
[1, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
]

player = Player(100, SCREEN_HIGHT - 130)
world = World(world_data)

# Game loop
while True:
    # Quit Handler
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        
    #<print(world.tile_list)

    # Drawing level
    screen.blit(bg_img, (0,0))
    screen.blit(sun_img,(100,100))
    world.draw()
    player.update()

    pygame.display.update()
    clock.tick(FPS)