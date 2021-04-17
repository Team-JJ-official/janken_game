from screen import Screen

class Game:
    class Gameplayer:
        def __init__(self):
            self.player = None
            self.character = None
            self.stock = 0
    
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
        self.start_screen = SS
        self.character_select_screen = CSS
        self.stage_select_screen = SSS
        self.game_screen = GS
        self.result_screen = RS
        self.option_screen = OS

    def main(self):
        now = self.start_screen()
        while True:
            now.main()
            result = now.result
            if result == Screen.START:
                now = self.start_screen()
            elif result == Screen.CHARACTER_SELECT:
                now = self.character_select_screen(self.players, self.characters, self.gameplayer1, self.gameplayer2)
            elif result == Screen.STAGE_SELECT:
                now = self.stage_select_screen(self.stages, self.gamesetting)
            elif result == Screen.GAME:
                now = self.game_screen(self.gameplayer1, self.gameplayer2, self.gamesetting)
            elif result == Screen.RESULT:
                now = self.result_screen(self.gameplayer1, self.gameplayer2, self.gamesetting)
            elif result == Screen.OPTION:
                now = self.option_screen()






        