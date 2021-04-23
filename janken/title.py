from typing import Dict, List, Callable, Tuple
from enum import Enum
import math
import random

import pygame
from pygame.locals import Rect
from pygame.sprite import Sprite

from stage import Stage
from screen import Screen, BaseScreen
from sprites import make_animation_sprites, RichSprite, make_outline_splites
from game_config import GameConfig

class TitleScreen(BaseScreen):
    def __init__(self, game_config: GameConfig):
        super().__init__()

        self.components = game_config.components

        self.press_rects = []
        
        self.init()
    
    def init(self):
        self._set_title()
        self._set_start_btn()
    

    def _set_title(self):
        title_surfaces = self.components["title"]
        rect = self.display.get_rect()
        x = rect.w // 2
        y = rect.h // 3
        title_sprite = make_animation_sprites(x, y, images=title_surfaces, interval=3, multiple=1.0)
        self.middle_sprites.add(title_sprite)
    

    def _set_start_btn(self):
        start_btn_surfaces = self.components["start"]
        rect = self.display.get_rect()
        x = rect.w // 2
        y = rect.h * 2 // 3
        start_btn_sprite = RichSprite(x=x, y=y, images=start_btn_surfaces, interval=5, press_fnc=self._go_to_next_screen)
        self.middle_sprites.add(start_btn_sprite)
        outline_sprites = make_outline_splites(start_btn_sprite.rect, self.components["outline"], border_width=1)
        start_btn_sprite.change_enter_fnc(self._visible_sprites, (self.front_sprites, outline_sprites))
        start_btn_sprite.change_exit_fnc(self._invisible_sprites, (self.front_sprites, outline_sprites))
    

    def _visible_sprites(self, group: pygame.sprite.Group, sprites: List[Sprite]):
        print("enter")
        print(group, "に", sprites, "を追加")
        group.add(sprites)
    

    def _invisible_sprites(self, group: pygame.sprite.Group, sprites: List[Sprite]):
        print("exit")
        print(group, "から", sprites, "を削除")
        group.remove(sprites)
    

    def _go_to_next_screen(self, *args):
        print("go to character select screen")
        self.run = False
        self.next_screen = Screen.CHARACTER_SELECT

    
    def main(self):
        while self.run:
            self.get_events()

            self.update()
            self.draw()

            pygame.display.update()
            self.clock.tick(self.fps)



if __name__ == "__main__":
    import time
    pygame.init()
    pygame.display.set_mode((800, 800))
    game_config = GameConfig("./jsons/config.json")

    components = game_config.components

    title_screen = TitleScreen(game_config)
    title_screen.main()