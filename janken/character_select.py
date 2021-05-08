from typing import Dict, List, Tuple
import json
from enum import Enum

import pygame
import pygame.gfxdraw

from screen import Screen, BaseScreen
from sprites import SimpleSprite, TextSprite, HoverRect, RichSprite
from sprites import make_outline_splites as make_outline_sprites
from game_config import GameConfig
from character import Character
from player import Player
from transform import surface_fit_to_rect, to_hoverable

from group import Group, GroupSingle, LayeredGroup


class BadgeSpriteGroup(Group):
    class BadgeSprite(pygame.sprite.Sprite):
        """
        colorで内部を塗りつぶした半径rの円のspriteを作成する.

        rectの初期値は(left=0, top=0, width=height=r)
        """

        def __init__(self, r = 10, color = (255, 255, 255)):
            super().__init__()
            badge = pygame.Surface((2*r, 2*r))
            badge.set_colorkey(badge.get_at((0, 0)))
            pygame.gfxdraw.filled_circle(badge, r, r, r, color)
            self.rect = badge.get_rect()
            self.image = badge
    
    def replace_circle(self, image: pygame.surface.Surface):
        """[summary].

        Args:
            image (pygame.surface.Surface): [description].
        """
        sprite = SimpleSprite(rect=image.get_rect(), image=image)
        sprite.rect.center = self.badgesprite.center
        self.badgesprite.add(sprite)
        self.add(sprite)

    def replace_text(self, text = "", font_size = int(1e5), color = (0, 0, 0)):
        """[summary].

        Args:
            text (str, optional): [description]. Defaults to "".
            font_size ([type], optional): [description]. Defaults to int(1e5).
            color (tuple, optional): [description]. Defaults to (0, 0, 0).
        """
        if self.badgesprite.sprite.rect.height < font_size:
            font_size = int(2 ** 0.5 * self.badgesprite.sprite.rect.height)
        text_sprite = TextSprite(
            x = self.badgesprite.sprite.rect.centerx,
            y = self.badgesprite.sprite.rect.centery,
            text = text,
            font = pygame.font.Font(None, font_size),
            color = color,
            align = "center",
            vertical_align = "middle"
        )
        if 2 ** 0.5 * self.badgesprite.sprite.rect.width < text_sprite.rect.width:
            print("dekasugi")
            self.textsprite.sprite.add(None)
        self.textsprite.add(text_sprite)

    def __init__(self, r = 10, color = (255, 255, 255), text = "", font_size = int(1e5)):
        """[summary]

        Args:
            r (int, optional): [description]. Defaults to 10.
            color (tuple, optional): [description]. Defaults to (255, 255, 255).
            text (str, optional): [description]. Defaults to "".
            font_size ([type], optional): [description]. Defaults to int(1e5).
        """
        super().__init__()
        self.r = r
        self.badgesprite = GroupSingle(self.BadgeSprite(r, color))
        self.textsprite = GroupSingle(None)
        self.replace_text(text, font_size)
    
    def draw(self, surface):
        self.badgesprite.draw(surface)
        self.textsprite.draw(surface)
    
    @property
    def center(self):
        return self.badgesprite.sprite.rect.center

    @center.setter
    def center(self, center: Tuple[int, int]):
        self.badgesprite.sprite.rect.center = center
        self.textsprite.sprite.rect.center = center

class GamePlayerSetter(Group):
    def __init__(self, gameplayer, func):
        super().__init__()
        self.gameplayer = gameplayer
        self.keys = gameplayer.player.keybind.keys
        self.func = func
        self.func(gameplayer, 0)
        # self.characters = {key: character for key, character in zip(self.keys, characters)}
    
    def update(self):
        pressed_keys = pygame.key.get_pressed()
        for i, key in enumerate(self.keys):
            if pressed_keys[key]:
                self.func(self.gameplayer, i)

class CharacterSelectArea(LayeredGroup):
    def __init__(self, display_rect, characters, outline, gameplayer1, gameplayer2):
        super().__init__()
        self.characters = characters
        self.outline_image = outline
        self.gameplayer1 = gameplayer1
        self.gameplayer2 = gameplayer2
        self.margin_lr = 30
        self.margin_top = 30
        self.space = 20
        self.rect = pygame.rect.Rect(
            self.margin_lr,
            self.margin_top,
            display_rect.width - self.margin_lr * 2,
            max(100, display_rect.height // 2)
        )
        width = (self.rect.width - self.space * (len(self.characters) - 1)) // len(self.characters)
        height = self.rect.height
        self.character_rects = [pygame.rect.Rect(
            self.rect.left + i * (width + self.space),
            self.rect.top,
            width,
            height
        ) for i in range(len(self.characters))]
        self.character_to_rect = {}
        for character, rect in zip(self.characters, self.character_rects):
            character.face_image = surface_fit_to_rect(rect=rect, surface=character.face_image)
            sprite = RichSprite(rect.centerx, rect.centery, image=character.face_image)
            to_hoverable(sprite, self.outline_image, self.background_sprites)
            sprite.change_press_fnc(self._press_character, (character, rect))
            self.middle_sprites.add(sprite)
        self.badges = {
            gameplayer1: BadgeSpriteGroup(25, (200, 5, 5), "1"),
            gameplayer2: BadgeSpriteGroup(25, (5, 200, 5), "2")
        }
        self.front_sprites.add(self.badges.values())
        self.gameplayers = [GamePlayerSetter(gameplayer1, self._set_character), GamePlayerSetter(gameplayer2, self._set_character)]
        self.add(self.gameplayers)

    def _set_character(self, gameplayer, i):
        if i >= len(self.characters):
            return
        gameplayer.character = self.characters[i]
        self.badges[gameplayer].center = self.character_rects[i].topleft
        if self.gameplayer1.character == self.gameplayer2.character:
            c = self.badges[self.gameplayer1].center
            b = self.badges[self.gameplayer2]
            b.center = (c[0] + b.r * 2, c[1])
        else:
            if self.gameplayer2.character != None:
                self.badges[self.gameplayer2].center = self.character_rects[self.characters.index(self.gameplayer2.character)].topleft
        self.characters[i].select_voice.play()

    
    def _press_character(self, character: Character, rect: pygame.rect.Rect):
        self._set_character(self.gameplayer1, self.characters.index(character))


class CharacterSelectScreen(BaseScreen):
    def __init__(self, game_config, gameplayer1, gameplayer2):
        super().__init__()

        self.game_config = game_config
        self.players = list(self.game_config.players.values())
        self.characters = list(self.game_config.characters.values())
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

        self.outline_image = self.game_config.components["outline"]
        self.outline_image = pygame.transform.scale2x(self.outline_image)
        self.font_size = 40
        self.font = pygame.font.SysFont(None, self.font_size)

        self.character_select_area = CharacterSelectArea(self.display_rect, self.characters, self.outline_image, self.gameplayer1, self.gameplayer2)
        

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

    def _set_characters_area(self):
        self.middle_sprites.add(self.character_select_area)

    def _set_player_select_area(self):
        self.player_select_rect = pygame.rect.Rect(
            self.margin_lr,
            self.character_select_area.rect.bottomleft[1] + (self.display_rect.height - self.character_select_area.rect.bottomleft[1]) // 2,
            self.character_select_area.rect.width,
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
        self.bgm: pygame.mixer.Sound = self.game_config.sounds["menu"]
        self.bgm.set_volume(0.1)
        self.bgm.play()


    def _adapt_display(self):
        pygame.display.set_caption("Character Select")
        
        bg_image = self.game_config.components["background"]
        bg_image = pygame.transform.scale(bg_image, self.display_rect.size)
        bg_sprite = SimpleSprite(rect=self.display_rect, image=bg_image)
        self.background_sprites.add(bg_sprite)

        self._set_characters_area()
        self._set_player_select_area()
        self._set_next_btn()
        self._set_back_btn()

    def main(self):
        self._adapt_display()
        images = []
        super().main()
            
def main():
    from game_config import GameConfig
    pygame.init()
    pygame.display.set_mode((700, 700))
    gc = GameConfig("./jsons/config.json")
    css = CharacterSelectScreen(gc, {}, {})
    css.main()

if __name__ == '__main__':
    main()