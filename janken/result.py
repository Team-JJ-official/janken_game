from typing import Callable, Union, Any

import pygame

from screen import Screen, BaseScreen
from sprites import RichSprite, SimpleSprite, TextSprite, layout_rects
from group import Group, LayeredGroup
from transform import to_hoverable
from component import SimpleButton


class ResultScreen(BaseScreen):
    def __init__(self, game_config, game_player1, game_player2, game_setting):
        super().__init__()
        self.game_config = game_config
        self.game_player1 = game_player1
        self.game_player2 = game_player2
        self.game_setting = game_setting
        self.area_rects = layout_rects(self.display.get_rect(), 4, 3)
        self.init()

    def _go_to_screen(self, screen: Screen):
        self.next_screen = screen
        self.run = False

    def init(self):
        btn_area_rect = self.area_rects[5].union(self.area_rects[10])
        btn_rects = layout_rects(btn_area_rect, 1, 3, margin_vertical=30, padding=20)
        btn_params = [
            (btn_rects[0], "もっかい", Screen.GAME),
            (btn_rects[1], "Character Select", Screen.CHARACTER_SELECT),
            (btn_rects[2], "Go to Title", Screen.START)
        ]
        btns = [SimpleButton(width=rect.width, height=rect.height, text=text,  outline=self.game_config.components["outline"], func = self._go_to_screen, func_args=(screen,))
            for rect, text, screen in btn_params]
        for btn, rect in zip(btns, btn_rects):
            btn.rect.center = rect.center
            self.middle_sprites.add(btn)

    def _winner(self):
        if self.game_player1.stock == 0:
            if self.game_player2 == 0:
                return None
            return self.game_player2
        else:
            if self.game_player2 > 0:
                return None
            return self.game_player1
    
    

    
    


if __name__ == '__main__':
    from game_config import GameConfig
    pygame.init()
    pygame.display.set_mode((700, 700))
    gc = GameConfig("./jsons/config.json")
    rs = ResultScreen(gc, {}, {}, {})
    rs.main()