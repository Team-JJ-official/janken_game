import pygame

from screen import BaseScreen, Screen
from sprites import RichSprite
from component import SimpleButton

class OptionScreen(BaseScreen):
    def __init__(self, game_config):
        super().__init__()
        self.game_config = game_config
        self._set_return_btn()
    
    def _go_to_title(self):
        self.next_screen = Screen.START
        self.run = False

    def _set_return_btn(self):
        #SimpleButton(width=rect.width, height=rect.height, text="Return",  outline=self.game_config.components["outline"], func = self._go_to_title)
        font = pygame.font.Font(None, 60)
        textsurface = font.render("Return", True, (0, 0, 0))
        return_btn = RichSprite(*self.display.get_rect().bottomleft, align="left", vertical_align="bottom", image=textsurface)
        return_btn.rect.move_ip(10, -10)
        self.hoverable(return_btn, self.game_config.components["outline"], border_width=5)
        return_btn.change_press_fnc(self._go_to_title)
        self.middle_sprites.add(return_btn)
    

if __name__ == '__main__':
    from game_config import GameConfig
    pygame.init()
    pygame.display.set_mode((700, 700))
    gc = GameConfig("./jsons/config.json")
    os = OptionScreen(gc)
    os.main()

    
