import pygame

from screen import Screen, BaseScreen
from sprites import RichSprite, SimpleSprite
from component import PlayerStockIcon
from transform import surface_fit_to_rect
from game_config import GameConfig

class GameScreen(BaseScreen):
    def __init__(self, game_player1, game_player2, game_setting):
        super().__init__()
        game_config = GameConfig("./jsons/config.json")

        if game_player1 is None:
            self.game_player1 = get_sample_game_player(game_config, name="sample1")
        else:
            self.game_player1 = game_player1
            if game_player1.character is None or game_player1.player is None:
                self.game_player1 = get_sample_game_player(game_config, name="sample1")
        if game_player2 is None:
            self.game_player2 = get_sample_game_player(game_config, name="sample2")
        else:
            self.game_player2 = game_player2
            if game_player2.character is None or game_player2.player is None:
                self.game_player2 = get_sample_game_player(game_config, name="sample2")
        if game_setting is None:
            self.game_setting = get_sample_game_setting(game_config, stock=5)
        else:
            self.game_setting = game_setting

        self.font = pygame.font.Font(None, 60)

        self.init()
    
    def init(self):
        self._set_bg()
        self._init_game()
        self._set_player_icons()
        self._set_random_btn()
    
    def _set_bg(self):
        print(self.game_setting.stage)
        rect = self.display.get_rect()
        bg_image = self.game_setting.stage.image
        bg_image = surface_fit_to_rect(bg_image, rect)
        self.bg_sprite = SimpleSprite(rect, bg_image)
        self.background_sprites.add(self.bg_sprite)

    def _init_game(self):
        self.game_player1.stock = self.game_setting.stock
        self.game_player2.stock = self.game_setting.stock


    def _set_player_icons(self):
        rect = self.display.get_rect()
        self.players_rect = pygame.rect.Rect(0, rect.h * 3 // 4, rect.w, rect.h // 4)
        game_players = [self.game_player1, self.game_player2]
        for i, game_player in enumerate(game_players):
            player_icon_sprite = PlayerStockIcon(
                left=self.players_rect.left + self.players_rect.w // len(game_players) * i,
                top=self.players_rect.top,
                game_player=game_player,
                image_height=100
            )
            self.middle_sprites.add(player_icon_sprite)
    
    def _set_random_btn(self):
        rect = self.display.get_rect()
        surface = self.font.render("random result", True, (255, 255, 255), (0, 0, 0))
        random_result_btn = RichSprite(rect.w//2, rect.h // 3, image=surface, press_fnc=self._random_result)
        self.middle_sprites.add(random_result_btn)
    
    def _count_down_stock(self, game_player):
        if game_player.stock > 0:
            game_player.stock -= 1
    
    def _random_result(self):
        import random
        players = [self.game_player1, self.game_player2]
        win_i = random.randint(0, 1)
        players[win_i].stock = 1
        players[(win_i + 1) % 2].stock = 0

        print("player {} win.".format(players[win_i].player.name))

        self.run = False
        self.next_screen = Screen.RESULT


def get_sample_game_player(game_config, name: str="sample", stock: int=0):
    import random

    from player import Player


    player = Player(_id=random.randint(0, 10000), name=name, matches_num=1, win_num=1)

    game_config = GameConfig("./jsons/config.json")

    class GamePlayer:
        def __init__(self):
            self.player = None
            self.character = None
            self.stock = 0

    game_player = GamePlayer()
    game_player.character = game_config.characters["0"]
    game_player.player = player
    game_player.stock = stock

    return game_player

def get_sample_game_setting(game_config, stock: int=3):
    import random

    class GameSetting:
        def __init__(self):
            self.stage = None
            self.stock = 0
        
    game_setting = GameSetting()
    game_setting.stage = random.choice(list(game_config.stages.values()))
    game_setting.stock = stock

    return game_setting


if __name__ == "__main__":
    pygame.init()
    pygame.display.set_mode((500, 500))

    from game_config import GameConfig
    game_config = GameConfig("./jsons/config.json")

    game_setting = get_sample_game_setting(game_config, stock=3)
    game_player1 = get_sample_game_player(game_config, name="sample1", stock=0)
    game_player2 = get_sample_game_player(game_config, name="sample2", stock=0)
    gs = GameScreen(game_player1, game_player2, game_setting)
    gs.main()