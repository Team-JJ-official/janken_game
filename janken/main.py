from screen import Screen
from loading import LoadingScreen
from title import TitleScreen
from stage_select import StageSelectScreen
from character_select import CharacterSelectScreen
from option import OptionScreen
from game import GameScreen
from result import ResultScreen

class Game:
    class Gameplayer:
        def __init__(self):
            self.player = None
            self.character = None
            self.stock = 0
        
        def __repr__(self):
            return self.player.name
    
    class Gamesetting:
        def __init__(self):
            self.stage = None
            self.stock = 0

    def __init__(self):
        self.gameplayer1 = self.Gameplayer()
        self.gameplayer2 = self.Gameplayer()
        self.gamesetting = self.Gamesetting()
        self.players = {}
        self.characters = {}
        self.stages = {}
        self.loading_screen = LoadingScreen
        self.start_screen = TitleScreen
        self.character_select_screen = CharacterSelectScreen
        self.stage_select_screen = StageSelectScreen
        self.game_screen = GameScreen
        self.result_screen = ResultScreen
        self.option_screen = OptionScreen

    def main(self):
        try:
            loading_screen = self.loading_screen()
            loading_screen.main()

            self.game_config = loading_screen.game_config
        except:
            print("Loading not done.")
            return
        self.gameplayer1.player = self.game_config.players["0"]
        self.gameplayer2.player = self.game_config.players["1"]
        now = self.start_screen(self.game_config)
        while True:
            now.main()
            next_screen = now.next_screen
            if next_screen == Screen.START:
                now = self.start_screen(self.game_config)
            elif next_screen == Screen.CHARACTER_SELECT:
                now = self.character_select_screen(self.game_config, self.gameplayer1, self.gameplayer2)
            elif next_screen == Screen.STAGE_SELECT:
                now = self.stage_select_screen(self.game_config, self.gamesetting)
            elif next_screen == Screen.GAME:
                now = self.game_screen(self.gameplayer1, self.gameplayer2, self.gamesetting)
            elif next_screen == Screen.RESULT:
                now = self.result_screen(self.game_config, self.gameplayer1, self.gameplayer2, self.gamesetting)
            elif next_screen == Screen.OPTION:
                now = self.option_screen(self.game_config)
            elif next_screen == Screen.QUIT:
                break


if __name__ == "__main__":
    # import pygame
    # pygame.init()
    # pygame.display.set_mode((700, 700))
    game = Game()
    game.main()





        