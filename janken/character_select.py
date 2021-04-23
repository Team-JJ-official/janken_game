from typing import Dict
import json

import pygame

from screen import Screen, BaseScreen
from sprites import SimpleSprite, TextSprite, HoverRect, make_outline_splites
from character import Character
from player import Player


class CharacterSelectScreen(BaseScreen):
    def __init__(self, players: Dict[str, Player], characters: Dict[str, Character], gameplayer1, gameplayer2):
        super().__init__()

        self.players = players.values()
        self.characters = characters.values()
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

        self.outline_image = pygame.image.load("./images/outline.png").convert()

    def _visible_outlines(self, hover_rect: HoverRect):
        """ hover_rect に対応した OutlineSprite を見えるようにする (self.middle_spritesに追加)
        """
        outline_sprites = self.hover_rects[hover_rect]
        self.middle_sprites.add(outline_sprites)
     
    def _invisible_outlines(self, hover_rect: HoverRect):
        """ hover_rect に対応した OutlineSprite を見えないようにする (self.middle_spritesから削除)
        """
        outline_sprites = self.hover_rects[hover_rect]
        self.middle_sprites.remove(outline_sprites)

    def _to_outlinable(self, rect: pygame.rect.Rect):
        outline = make_outline_splites(rect, self.outline_image)
        self.hover_rects[rect] = outline



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
            splite = SimpleSprite(rect, character.face_image)
            self.front_sprites.add(splite)

    def _set_player_select(self):
        self.player_select_rect = pygame.rect.Rect(
            self.margin_lr,
            self.character_select_rect.bottomleft[0] + (self.display_rect.height - self.character_select_rect.bottomleft[0]) // 2,
            self.character_select_rect.width,
            30
        )
        left = TextSprite(
            x=self.player_select_rect.left,
            y=self.player_select_rect.y,
            text="Player 1",
            font=self.font,
            color=(0, 0, 0),
            align="left",
            vertical_align="middle",
        )


    def _adapt_display(self):
        pygame.display.set_caption("Character Select")
        
        bg_image = pygame.image.load("./images/bg.jpeg")
        bg_image = pygame.transform.scale(bg_image, self.display_rect.size)
        bg_sprite = SimpleSprite(rect=self.display_rect, image=bg_image)
        self.background_sprites.add(bg_sprite)

        self._set_characters()
        self._set_player_select()


    def main(self):
        self._adapt_display()
        images = []
        while self.run:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.next_screen = Screen.QUIT
                    self.run = False
            self.draw()
            pygame.display.update()
            self.clock.tick(self.fps)
            
def main():
    from game_config import GameConfig
    pygame.init()
    pygame.display.set_mode((700, 700))
    gc = GameConfig("./jsons/config.json")
    gc.characters["1"] = gc.characters["0"]
    css = CharacterSelectScreen({}, gc.characters, {}, {})
    css.main()

if __name__ == '__main__':
    main()