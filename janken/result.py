from typing import Callable, Union, Any

import pygame

from screen import Screen, BaseScreen
from sprites import RichSprite, SimpleSprite, TextSprite, layout_rects
from group import Group, LayeredGroup
from transform import to_hoverable

class SimpleButton(LayeredGroup):
    def __init__(self, width: int = 300, height: int = 100, text: str = "", outline = None, func: Callable = None, func_args: Any = None):
        super().__init__()
        self.text = text
        self.font_size = height // 2
        self.font = pygame.font.Font("./fonts/Mplus2-Medium.ttf", self.font_size)
        self.func = func
        self.func_args = func_args
        self.__text_height_scale = 1.0
        self.width = width
        self.height = height
        self.frame_sprite =  pygame.sprite.Sprite()
        self.text_sprite =  pygame.sprite.Sprite()
        self.outline = outline
        self.baserect = pygame.rect.Rect(0, 0, self.width, self.height)
        self.rect = pygame.rect.Rect(0, 0, self.width, self.height)
        self.init()
    
    def _fit_font(self):
        while self.font.size(self.text)[0] > self.width:
            self.font_size -= 1
            self.font = pygame.font.Font("./fonts/Mplus2-Medium.ttf", self.font_size)
    
    def _set_frame(self, clear = True, image = None):
        if image == None:
            btn_image = pygame.Surface((self.width, self.height))
            btn_image.fill((200, 200, 200))
            if clear:
                btn_image.set_colorkey(btn_image.get_at((0, 0)))
            self.frame_sprite = RichSprite(0, 0, image = btn_image, align = "left", vertical_align="top")
        else:
            btn_image = pygame.transform.smoothscale(image, (self.width, self.height))
            self.frame_sprite = RichSprite(0, 0, image = btn_image, align = "left", vertical_align="top")
        self.frame_sprite.change_press_fnc(self.func, self.func_args)

    def _set_text(self):
        self.text_sprite = TextSprite(0, 0, text=self.text, font=self.font)
        self.text_sprite.rect.center = self.baserect.center
    
    def init(self):
        self._fit_font()
        self._set_text()
        self._set_frame(clear=False)
        self.outline = pygame.transform.scale2x(self.outline)
        self.outline = pygame.transform.scale2x(self.outline)
        
        self.outlines = to_hoverable(self.frame_sprite, self.outline, self.middle_sprites)
        self.background_sprites.add(self.frame_sprite)
        self.middle_sprites.add(self.text_sprite)

    def update(self):
        if self.baserect.topleft != self.rect.topleft:
            dx = self.rect.left - self.baserect.left
            dy = self.rect.top - self.baserect.top
            self.baserect.topleft = self.rect.topleft
            for sprites in [self.middle_sprites, self.background_sprites]:
                for sprite in sprites:
                    sprite.rect.move_ip(dx, dy)
            if not self.middle_sprites.has(self.outlines):
                for sprite in self.outlines:
                    sprite.rect.move_ip(dx, dy)
        super().update()


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