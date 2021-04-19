from enum import Enum

import pygame

class Screen(Enum):
    START = 0
    CHARACTER_SELECT = 1
    STAGE_SELECT = 2
    GAME = 3
    RESULT = 4
    OPTION = 5
    QUIT = 6

class BaseScreen:
    def __init__(self):
        if not pygame.init():
            pygame.init()
            pygame.display.set_mode((500, 500))
            pygame.display.set_caption("sample")
        self.display = pygame.display.get_surface()
        self.front_sprites = pygame.sprite.Group()
        self.middle_sprites = pygame.sprite.Group()
        self.background_sprites = pygame.sprite.Group()
        self.fps = 60
        self.delta_time = 1 / self.fps
        self.clock = pygame.time.Clock()
        self.run = True
        self.next_screen = Screen.QUIT
    
    def empty_all_sprites(self):
        self.background_sprites.empty()
        self.middle_sprites.empty()
        self.front_sprites.empty()
    
    def update(self):
        self.background_sprites.update()
        self.middle_sprites.update()
        self.front_sprites.update()

    def draw(self):
        self.display.fill((255, 255, 255))
        self.background_sprites.draw(self.display)
        self.middle_sprites.draw(self.display)
        self.front_sprites.draw(self.display)