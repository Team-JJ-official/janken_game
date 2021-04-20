from typing import Dict

import pygame

from screen import Screen
from character import Character
from player import Player

class CharacterSelectScreen:
    def __init__(self, players: Dict[str, Player], characters: Dict[str, Character], gameplayer1, gameplayer2):
        self.display = pygame.display.get_surface()
        self.result = Screen.STAGE_SELECT
        self.fps = 60

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

    def _adapt_display(self):
        pygame.display.set_caption("Character Select")
        
        self.character_select_rect = pygame.rect.Rect(
            self.margin_lr,
            self.margin_top,
            self.display_rect.width - self.margin_lr * 2,
            max(100, self.display_rect.height // 2)
        )
        self.player_select_rect = pygame.rect.Rect(
            self.margin_lr,
            self.character_select_rect.bottomleft[0] + (self.display_rect.height - self.character_select_rect.bottomleft[0]) // 2,
            self.character_select_rect.width,
            30
        )

        width = (self.character_select_rect.width - self.space * (len(self.characters) - 1)) // len(self.characters)
        height = self.character_select_rect.height
        self.character_rects = [pygame.rect.Rect(
            self.character_select_rect.left + i * (width + self.space),
            self.character_select_rect.top,
            width,
            height
        ) for i in range(len(self.characters))]

    def main(self):
        clock = pygame.time.Clock()
        self._adapt_display()
        while True:
            for character, rect in zip(self.characters, self.character_rects):
                img = pygame.transform.scale(character.face_image, (rect.width, rect.height))
                self.display.blit(img, (rect.left, rect.top))
            pygame.display.update()
            clock.tick(self.fps)
            
def main():
    import os
    pygame.init()
    pygame.display.set_mode((700, 700))
    image = pygame.image.load(os.path.join("images", "stage_0.png")).convert()
    characters = {}
    for i in range(4):
        characters[str(i)] = Character(i, "a")
        characters[str(i)].set_face_image(image)
    css = CharacterSelectScreen({}, characters, {}, {})
    css.main()

if __name__ == '__main__':
    main()