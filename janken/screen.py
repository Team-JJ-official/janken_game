from enum import Enum

import pygame

from sprites import make_outline_splites
from group import Group as MyGroup

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
        if not pygame.display.get_surface():
            pygame.display.set_mode((500, 500))
            pygame.display.set_caption("sample")
        self.display = pygame.display.get_surface()
        # self.front_sprites = pygame.sprite.Group()
        # self.middle_sprites = pygame.sprite.Group()
        # self.background_sprites = pygame.sprite.Group()
        self.front_sprites = MyGroup()
        self.middle_sprites = MyGroup()
        self.background_sprites = MyGroup()
        # self.groups = [pygame.sprite.Group() for i in range(9)]
        self.fps = 60
        self.delta_time = 1 / self.fps
        self.clock = pygame.time.Clock()
        self.run = True
        self.next_screen = Screen.QUIT
        self.key_downs = []
    
    # @property
    # def front_sprites(self) -> pygame.sprite.Group:
    #     return self.groups[7]
    
    # @property
    # def middle_sprites(self) -> pygame.sprite.Group:
    #     return self.groups[4]
    
    # @property
    # def background_sprites(self) -> pygame.sprite.Group:
    #     return self.groups[1]
    
    def hoverable(self, rich_sprite, outline_image, group=None, border_width: int=5):
        if group is None:
            group = self.middle_sprites
        outlines = make_outline_splites(rich_sprite.rect, outline_image, border_width=border_width)
        rich_sprite.change_enter_fnc(group.add, (outlines,))
        rich_sprite.change_exit_fnc(group.remove, (outlines,))
    
    def get_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.run = False
            elif event.type == pygame.KEYDOWN:
                self.key_downs.append(event)
    
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
    
    def main(self):
        while self.run:
            self.get_events()
            self.update()
            self.draw()
            pygame.display.update()
            self.clock.tick(self.fps)

        # for group in self.groups:
        #     if len(group):
        #         group.draw(self.display)