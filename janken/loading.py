from typing import Dict, List, Callable, Tuple
from enum import Enum
import math
import random

import pygame
from pygame.locals import Rect
from pygame.sprite import Sprite

from stage import Stage
from screen import Screen, BaseScreen
from sprites import SimpleSprite, TextSprite, AlignSprite, load_animation_sprite

class Loading(BaseScreen):
    def __init__(self):
        super().__init__()
        self.result = Screen.START
        self.fps = 60

        bg_image = pygame.image.load("./images/bg.jpeg")
        bg_sprite = SimpleSprite(bg_image.get_rect(), bg_image)
        self.background_sprites.add(bg_sprite)

        # logo = pygame.image.load("./images/loading.png")
        # rect = logo.get_rect()
        # logo = pygame.transform.scale(logo, (int(rect.w * 0.7), int(rect.h * 0.7)))
        # rect = logo.get_rect()
        # rect.center = self.display.get_rect().center
        # logo = SimpleSprite(rect, logo)
        # # logo = AlignSprite(
        # #     x=rect.centerx,
        # #     y=rect.centery,
        # #     image=logo,
        # #     align="center",
        # #     vertical_align="middle",
        # # )
        # self.middle_sprites.add(logo)
        x, y = self.display.get_rect().center
        loading_sprits = load_animation_sprite(x, y, "./images/loading/", interval=20, multiple=0.7)
        self.middle_sprites.add(loading_sprits)
    
    def main(self):
        for i in range(600):
            self.update()
            self.draw()
            pygame.display.update()
            self.clock.tick(60)
        pygame.font.init()
        # 全てのローディング

if __name__ == "__main__":
    pygame.init()
    pygame.display.set_mode((500, 500))
    loading = Loading()
    loading.main()