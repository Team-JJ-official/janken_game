from typing import Callable, Union, Any

import pygame

from screen import Screen, BaseScreen
from sprites import RichSprite, SimpleSprite, TextSprite, layout_rects
from group import Group, LayeredGroup
from transform import to_hoverable
from component import SimpleButton

class ResultText(Group):
    def __init__(self, game_player1, game_player2, rect) -> None:
        super().__init__()
        self.winner = self._winner(game_player1, game_player2)
        if self.winner is None:
            self.text = "DRAW"
        else:
            self.text = self.winner.player.name + " WIN!!"
            self.winner.player.win_num += 1
        
        game_player1.player.matches_num += 1
        game_player2.player.matches_num += 1

        self.rect = rect
        self.font_size = self.rect.height // 3
        textsprite = TextSprite(
            x = self.rect.centerx,
            y = self.rect.centery,
            text = self.text,
            font = pygame.font.Font("./fonts/Mplus2-Medium.ttf", self.font_size),
            align = "center",
            vertical_align = "middle"
        )
        textsprite.center = self.rect.center
        self.add(textsprite)

    def _winner(self, game_player1, game_player2):
        if game_player1.stock == 0:
            if game_player2.stock == 0:
                return None
            return game_player2
        else:
            if game_player2.stock > 0:
                return None
            return game_player1


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
        bg_image = self.game_config.components["background"]
        bg_image = pygame.transform.scale(bg_image, self.display.get_rect().size)
        bg_sprite = SimpleSprite(rect=self.display.get_rect(), image=bg_image)
        self.background_sprites.add(bg_sprite)

        result_area_rect = self.area_rects[0].union(self.area_rects[3])
        result_area = ResultText(self.game_player1, self.game_player2, result_area_rect)
        self.middle_sprites.add(result_area)

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


if __name__ == '__main__':
    from game_config import GameConfig
    from game import get_sample_game_player
    pygame.init()
    pygame.display.set_mode((700, 700))

    gc = GameConfig("./jsons/config.json")
    game_player1 = get_sample_game_player(gc, name="sample1", stock=1)
    game_player2 = get_sample_game_player(gc, name="sample2", stock=0)
    rs = ResultScreen(gc, game_player1, game_player2, {})
    rs.main()