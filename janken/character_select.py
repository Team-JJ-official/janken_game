from typing import Dict, List
import json

import pygame
import pygame.gfxdraw

from screen import Screen, BaseScreen
from sprites import SimpleSprite, TextSprite, HoverRect, RichSprite
from sprites import make_outline_splites as make_outline_sprites
from game_config import GameConfig
from character import Character
from player import Player
from transform import surface_fit_to_rect

from group import Group, GroupSingle


class BadgeSpriteGroup(Group):
    """
    背景と文字のspriteを1組のみ持つクラス\\
    """
    class BadgeSprite(pygame.sprite.Sprite):
        """
        colorで内部を塗りつぶした半径rの円のspriteを作成する\\
        rectの初期値は(left=0, top=0, width=height=r)\\
        """
        def __init__(self, r = 10, color = (255, 255, 255)):
            super().__init__()
            badge = pygame.Surface((2*r, 2*r))
            badge.set_colorkey(badge.get_at((0, 0)))
            pygame.gfxdraw.filled_circle(badge, r, r, r, color)
            self.rect = badge.get_rect()
            self.image = badge
    
    def replace_circle(self, image: pygame.surface.Surface):
        sprite = SimpleSprite(rect=image.get_rect(), image=image)
        sprite.rect.center = self.badge_sprite.center
        self.badge_sprite.add(sprite)
        self.add(sprite)

    def replace_text(self, text = "", font_size = int(1e5), color = (0, 0, 0)):
        if self.badge.sprite.rect.height < font_size:
            font_size = int(2 ** 0.5 * self.badge.sprite.rect.height)
        text_sprite = TextSprite(
            x = self.badge.sprite.rect.centerx,
            y = self.badge.sprite.rect.centery,
            text = text,
            font = pygame.font.Font(None, font_size),
            color = color,
            align = "center",
            vertical_align = "middle"
        )
        if 2 ** 0.5 * self.badge.sprite.rect.width < text_sprite.rect.width:
            print("dekasugi")
            self.text.sprite.add(None)
        self.text.add(text_sprite)
        self.add(self.text)

    def __init__(self, r = 10, color = (255, 255, 255), text = "", font_size = int(1e5)):
        super().__init__()
        self.badge = GroupSingle(self.BadgeSprite(r, color))
        self.text = GroupSingle(None)
        self.text = self.replace_text(text, font_size)
        self.add(self.badge)
    

class BaseScreen2(BaseScreen):
    def __init__(self):
        super().__init__()
        self.groups = [Group() for i in range(9)]


class CharacterSelectScreen(BaseScreen2):
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
        self.badge1 = BadgeSpriteGroup(25, (200, 5, 5), "1")
        # self.badge2 = BadgeSprite(25)
        # self.badge2.rect.center = (0, 50)

        self.outline_image = pygame.image.load("./images/components/outline.png").convert()
        self.outline_image = pygame.transform.scale2x(self.outline_image)
        self.outline_image = pygame.transform.scale2x(self.outline_image)
        self.font_size = 40
        self.font = pygame.font.SysFont(None, self.font_size)

    def _badge_sprite(self, color):
        badge = pygame.Surface((50, 50))
        badge.set_colorkey(badge.get_at((0, 0)))
        pygame.gfxdraw.filled_circle(badge, badge.get_width() // 2, badge.get_height() // 2, 20, color)
        return SimpleSprite(badge.get_rect(), badge)

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

    def _press_character(self, character: Character, rect: pygame.rect.Rect):
        character.select_voice.play()

    def _set_characters_area(self):
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
            # character.face_image = pygame.transform.scale(character.face_image, rect.size)
            character.face_image = surface_fit_to_rect(rect=rect, surface=character.face_image)
            sprite = RichSprite(rect.centerx, rect.centery, image=character.face_image)
            self.hoverable(sprite, self.outline_image)
            sprite.change_press_fnc(self._press_character, (character, rect))
            self.front_sprites.add(sprite)

    def _set_player_select_area(self):
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
        print(self.front_sprites)
        self.front_sprites.add(self.badge1)
        print(self.front_sprites)
        print(self.front_sprites.sprites())

        self._set_characters_area()
        self._set_player_select_area()
        self._set_next_btn()
        self._set_back_btn()
        self._set_bgm()

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