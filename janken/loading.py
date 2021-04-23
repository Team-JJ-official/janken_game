from typing import Dict, List, Callable, Tuple
from enum import Enum
import math
import random
from threading import Thread

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

        bg_image = pygame.image.load("./images/components/bg.jpeg").convert_alpha()
        bg_sprite = SimpleSprite(bg_image.get_rect(), bg_image)
        self.background_sprites.add(bg_sprite)

        x, y = self.display.get_rect().center
        loading_sprits = load_animation_sprite(x, y, "./images/components/loading", interval=20, multiple=0.7)
        self.middle_sprites.add(loading_sprits)
    
    def init(self):
        """全てのローディング処理
        """
        import time
        pygame.font.init()
        time.sleep(4)
        self.run = False
        self.next_screen = Screen.START
    
    def main(self):
        # 全てのローディングはスレッドで
        thread = Thread(target=self.init)
        thread.start()
        while self.run:
            self.get_events()
            self.update()
            self.draw()
            pygame.display.update()
            self.clock.tick(60)

if __name__ == "__main__":
    pygame.init()
    pygame.display.set_mode((500, 500))
    loading = Loading()
    loading.main()