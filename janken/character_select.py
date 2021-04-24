from typing import Dict, List
import json

import pygame

from screen import Screen, BaseScreen
from sprites import SimpleSprite, TextSprite, HoverRect, RichSprite
from sprites import make_outline_splites as make_outline_sprites
from game_config import GameConfig
from character import Character
from player import Player


class CharacterSelectScreen(BaseScreen):
    def __init__(self, game_config, gameplayer1, gameplayer2):
        super().__init__()

        self.game_config = game_config
        self.players = {}
        self.characters = self.game_config.characters.values()
        self.gameplayer1 = gameplayer1
        self.gameplayer2 = gameplayer2

        self.margin_lr = 30
        self.margin_top = 30
        self.display_rect = self.display.get_rect()
        self.character_select_rect = None
        self.player_select_rect = None
        self.character_rects = []
        self.space = 20
        self.hover_rects = {}

        self.outline_image = pygame.image.load("./images/components/outline.png").convert()
        self.outline_image = pygame.transform.scale2x(self.outline_image)
        self.outline_image = pygame.transform.scale2x(self.outline_image)
        self.font_size = 40
        self.font = pygame.font.SysFont(None, self.font_size)

    def _goto_stage_select(self):
        self.next_screen = Screen.STAGE_SELECT
        self.run = False

    def _goto_title(self):
        self.next_screen = Screen.START
        self.run = False


    def _set_next_btn(self):
        next_btn_image = self.font.render("Next", True, (0, 0, 0))
        next_btn = RichSprite(*self.display_rect.bottomright, image=next_btn_image, align="right", vertical_align="bottom")
        next_btn.rect.move_ip(-5, -5)
        outline = make_outline_sprites(next_btn.rect, self.outline_image)
        next_btn.change_enter_fnc(self.middle_sprites.add, outline)
        next_btn.change_exit_fnc(self.middle_sprites.remove, outline)
        next_btn.change_press_fnc(self._goto_stage_select)
        self.front_sprites.add(next_btn)
    
    def _set_back_btn(self):
        back_btn_image = self.font.render("Back", True, (0, 0, 0))
        back_btn = RichSprite(*self.display_rect.bottomleft, image=back_btn_image, align="left", vertical_align="bottom")
        back_btn.rect.move_ip(5, -5)
        outline = make_outline_sprites(back_btn.rect, self.outline_image)
        back_btn.change_enter_fnc(self.middle_sprites.add, outline)
        back_btn.change_exit_fnc(self.middle_sprites.remove, outline)
        back_btn.change_press_fnc(self._goto_title)
        self.front_sprites.add(back_btn)

    def _press_character(self, character: Character):
        character.select_voice.play()

    def _set_characters(self):
        self.character_select_rect = pygame.rect.Rect(
            self.margin_lr,
            self.margin_top,
            self.display_rect.width - self.margin_lr * 2,
            max(100, self.display_rect.height // 2)
        )
        width = (self.character_select_rect.width - self.space * (len(self.characters) - 1)) // len(self.characters)
        height = self.character_select_rect.height
        self.character_rects = [pygame.rect.Rect(
            self.character_select_rect.left + i * (width + self.space),
            self.character_select_rect.top,
            width,
            height
        ) for i in range(len(self.characters))]
        for character, rect in zip(self.characters, self.character_rects):
            character.face_image = pygame.transform.scale(character.face_image, rect.size)
            sprite = RichSprite(rect.centerx, rect.centery, image=character.face_image)
            outline = make_outline_sprites(rect, self.outline_image)
            sprite.change_enter_fnc(self.middle_sprites.add, (outline,))
            sprite.change_exit_fnc(self.middle_sprites.remove, (outline,))
            sprite.change_press_fnc(self._press_character, (character,))
            self.front_sprites.add(sprite)

    def _set_player_select(self):
        self.player_select_rect = pygame.rect.Rect(
            self.margin_lr,
            self.character_select_rect.bottomleft[1] + (self.display_rect.height - self.character_select_rect.bottomleft[1]) // 2,
            self.character_select_rect.width,
            30
        )
        left = TextSprite(
            x=self.player_select_rect.left,
            y=self.player_select_rect.y,
            text="Player 1",
            font=self.font,
            color=(0, 0, 0),
            bgcolor=(255, 255, 255),
            align="left",
            vertical_align="middle",
        )
        self.front_sprites.add(left)

    def _set_bgm(self):
        sounds = self.game_config.sounds
        bgm = sounds["menu"]
        bgm.set_volume(0.1)
        bgm.play()

        


    def _adapt_display(self):
        pygame.display.set_caption("Character Select")
        
        bg_image = pygame.image.load("./images/components/bg.jpeg")
        bg_image = pygame.transform.scale(bg_image, self.display_rect.size)
        bg_sprite = SimpleSprite(rect=self.display_rect, image=bg_image)
        self.background_sprites.add(bg_sprite)

        self._set_characters()
        self._set_player_select()
        self._set_next_btn()
        self._set_back_btn()
        self._set_bgm()

    def draw(self):
        for hover_rect in self.hover_rects.keys():
            hover_rect.update()
        super().draw()

    def main(self):
        self._adapt_display()
        images = []
        while self.run:
            self.get_events()
            self.update()
            self.draw()
            pygame.display.update()
            self.clock.tick(self.fps)
            
def main():
    from game_config import GameConfig
    pygame.init()
    pygame.display.set_mode((700, 700))
    gc = GameConfig("./jsons/config.json")
    gc.characters["1"] = gc.characters["0"]
    css = CharacterSelectScreen(gc, {}, {})
    css.main()

if __name__ == '__main__':
    main()