from typing import Dict, List, Callable, Tuple
from enum import Enum
import math
import random
import time
from threading import Thread

import pygame
from pygame.locals import Rect
from pygame.sprite import Sprite

from stage import Stage
from screen import Screen, BaseScreen
from sprites import SimpleSprite, TextSprite, AlignSprite, load_animation_sprite
from game_config import GameConfig

class LoadingScreen(BaseScreen):
    def __init__(self):
        super().__init__()
        self.result = Screen.START
        self.fps = 60

        self.game_config = None

        bg_image = pygame.image.load("./images/components/bg.jpeg").convert_alpha()
        bg_sprite = SimpleSprite(bg_image.get_rect(), bg_image)
        self.background_sprites.add(bg_sprite)

        x, y = self.display.get_rect().center
        loading_sprits = load_animation_sprite(x, y, "./images/components/loading", interval=20, multiple=0.7)
        self.middle_sprites.add(loading_sprits)
    
    def init(self):
        """全てのローディング処理
        """
        time.sleep(2)
        pygame.font.init()
        self.game_config = GameConfig("./jsons/config.json")
        self.run = False
        self.next_screen = Screen.START
    
    def main(self):
        # 全てのローディングはスレッドで
        thread = Thread(target=self.init)
        thread.start()
        super().main()

if __name__ == "__main__":
    from stage_select import StageSelectScreen
    from title import TitleScreen

    pygame.init()
    pygame.display.set_mode((500, 500))
    loading = LoadingScreen()
    loading.main()

    game_config = loading.game_config

    start_screen = TitleScreen(game_config)
    start_screen.main()

    stage_select_screen = StageSelectScreen(game_config, None)
    stage_select_screen.main()
